# encoding: utf-8

import asyncio
import logging
import typing
from random import randint

import discord
from discord.ext import commands
from lifesaver.bot import command, Cog, Context
from lifesaver.utils.formatting import truncate
from lifesaver.utils.timing import Timer, format_seconds

log = logging.getLogger(__name__)
SendVerdict = typing.Tuple[bool, typing.Optional[Exception]]


def bold_timer(timer: Timer) -> str:
    if timer.duration > 1:
        return f'**{timer}**'
    else:
        return str(timer)


class Health(Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(bot, *args, **kwargs)

        self.rtt_sends = {}
        self.rtt_edits = {}

    async def on_message_edit(self, message, _message):
        event = self.rtt_edits.get(message.id)
        if event:
            log.debug('RTT: Received edit_rx for %d.', message.id)
            event.set()
            del self.rtt_edits[message.id]

    async def on_message(self, message):
        event = self.rtt_sends.get(message.nonce)
        if event:
            log.debug('RTT: Received send_rx for %d (nonce=%d).', message.id, message.nonce)
            event.set()
            del self.rtt_sends[message.nonce]

    @command(aliases=['p'])
    async def ping(self, ctx: Context):
        """Pings the bot."""
        await ctx.send('Pong!')

    @command()
    @commands.cooldown(3, 4, type=commands.BucketType.guild)
    async def rtt(self, ctx: Context):
        """Performs a full RTT to measure REST and gateway latency.

        "TX" refers to the time it takes for the HTTP request to be sent, and
        for a response to be received and processed.
        "RX" refers to the time it takes for the gateway to dispatch an action,
        for example "Edit RX" refers to the time between editing a message with
        the APIand the gateway dispatching a MESSAGE_UPDATE packet.
        """
        nonce = randint(1000, 10000)

        send_failed: SendVerdict = (False, None)
        edit_failed: SendVerdict = (False, None)

        # Send a message, and wait for it to come back.
        with Timer() as send:
            event = asyncio.Event()
            self.rtt_sends[nonce] = event

            with Timer() as send_tx:
                try:
                    message = await ctx.send('RTT: `\N{LOWER HALF BLOCK}`', nonce=nonce)
                except discord.HTTPException as error:
                    send_failed = (True, error)

            with Timer() as send_rx:
                await event.wait()

        # Edit a message, and wait for it to come back.
        with Timer() as edit:
            event = asyncio.Event()
            self.rtt_edits[message.id] = event

            with Timer() as edit_tx:
                try:
                    await message.edit(content='RTT: `\N{FULL BLOCK}`')
                except discord.HTTPException as error:
                    edit_failed = (True, error)

            with Timer() as edit_rx:
                await event.wait()

        avg_rx = (send_rx.duration + edit_rx.duration) / 2
        avg_tx = (send_tx.duration + edit_tx.duration) / 2

        slow = send.duration > 1 or edit.duration > 1

        def format_transfer(timer, tx, rx):
            timer = bold_timer(timer)
            tx = bold_timer(tx)
            rx = bold_timer(rx)

            return f'RTT: {timer}\n\nTX: {tx}\nRX: {rx}'

        embed = discord.Embed()
        embed.color = discord.Color.red() if slow else discord.Color.green()
        embed.title = 'RTT Results'

        embed.add_field(
            name='MESSAGE_CREATE',
            value=format_transfer(send, send_tx, send_rx),
        )
        embed.add_field(
            name='MESSAGE_UPDATE',
            value=format_transfer(edit, edit_tx, edit_rx),
        )
        embed.set_footer(
            text=f'Avg. TX: {format_seconds(avg_tx)}, RX: {format_seconds(avg_rx)}',
        )

        failures = {'Send': send_failed, 'Edit': edit_failed}

        if any(result[0] for (name, result) in failures.items()):
            content = '\n'.join(
                f'{name}: Failed with HTTP {result[1].code}: {truncate(result[1].message, 100)}'  # type: ignore
                for (name, result) in failures.items()
                if result[0] is not False
            )
            print('content:', content)
            embed.add_field(name='Failures', value=content, inline=False)

        await message.edit(content='', embed=embed)


def setup(bot):
    bot.add_cog(Health(bot))
