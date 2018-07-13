# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2017 - 2018 slice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import logging
from random import randint

import discord
from discord.ext import commands
from lifesaver.bot import command, Cog, Context
from lifesaver.utils.timing import Timer, format_seconds

log = logging.getLogger(__name__)


def bold_timer(timer):
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
        with Timer() as timer:
            message = await ctx.send('...')

        content = f'Pong! GW: `{ctx.bot.latency * 1000:.2f}ms`, REST: `{timer}`'
        await message.edit(content=content)

    @command()
    @commands.cooldown(3, 4, type=commands.BucketType.guild)
    async def rtt(self, ctx: Context):
        """
        Performs a full RTT to measure REST and gateway latency.

        "TX" refers to the time it takes for the HTTP request to be sent, and
        for a response to be received and processed.
        "RX" refers to the time it takes for the gateway to dispatch an action,
        for example "Edit RX" refers to the time between editing a message with
        the APIand the gateway dispatching a MESSAGE_UPDATE packet.
        """
        nonce = randint(1000, 10000)

        # send a message, then wait for the gateway to dispatch it to us
        with Timer() as send:
            event = asyncio.Event()
            self.rtt_sends[nonce] = event

            # send
            with Timer() as send_tx:
                message = await ctx.send('RTT: `\N{LOWER HALF BLOCK}`', nonce=nonce)

            # wait
            with Timer() as send_rx:
                await event.wait()

        # now edit the message, and wait for the gateway to dispatch that
        with Timer() as edit:
            event = asyncio.Event()
            self.rtt_edits[message.id] = event

            # edit
            with Timer() as edit_tx:
                await message.edit(content='RTT: `\N{FULL BLOCK}`')

            # wait
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

        await message.edit(content='', embed=embed)


def setup(bot):
    bot.add_cog(Health(bot))
