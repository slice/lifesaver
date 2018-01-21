from collections import defaultdict
from typing import List, Dict, Optional, Set, DefaultDict

import asyncio
import re

import discord
from discord.ext import commands

from lifesaver.bot import Cog, command, Context


PHRASE_REGEX = re.compile(r'[0-9A-Za-z ]+')


async def receive_phrase(ctx: Context, *, dm_from: discord.User) -> List[str]:
    while True:
        msg = await ctx.bot.wait_for(
            'message',
            check=lambda m: m.channel == dm_from.dm_channel and m.author == dm_from
        )

        if not PHRASE_REGEX.fullmatch(msg.content):
            await dm_from.send('Invalid phrase. Only use ASCII numbers, letters, and spaces. Please try again.')
            continue
        elif len(msg.content) > 280:
            await dm_from.send('The maximum amount of characters allowed is 280. Please try again.')
            continue
        elif not msg.content:
            await dm_from.send('You need to send some text. Please try again.')
            continue

        return list(msg.content.strip().upper())


async def game(ctx: Context, *, master: discord.User, binded_channel: discord.TextChannel):
    phrase: Optional[List[str]] = None
    points: Dict[int, int] = {}
    guesses: List[str] = []

    try:
        status_update = await binded_channel.send(
            f'Waiting for the master ({master}) to start the game...'
        )
    except discord.HTTPException:
        # cannot send in binded channel
        return

    try:
        await master.send(
            'Send me your phrase (numbers, letters, and spaces only)! Maximum of 280 characters.'
        )

        phrase = await receive_phrase(ctx, dm_from=master)

        await master.send(
            f'Okay, game started in {binded_channel.mention}! '
            'Send `cancel!` at any time in that channel to stop the game if you want.'
        )
    except discord.HTTPException:
        await ctx.send(f"{ctx.author.mention}: I can't DM you, game aborted.")
        return

    # replace all nonspaces with dashes to hide everything
    phrase_base: List[str] = list(re.sub(r'[^ ]', '-', ''.join(phrase)))

    suffix = '?'
    await status_update.edit(
        content=f'Game started! Guess with letters or phrases by adding a `{suffix}` suffix.'
    )
    game_message: discord.Message = await binded_channel.send(''.join(phrase_base))

    while True:
        incoming_message = await ctx.bot.wait_for(
            'message', check=lambda m: not m.author.bot and m.channel == binded_channel
        )

        if incoming_message.author == master and incoming_message.content == 'cancel!':
            await binded_channel.send("**Game cancelled.** That's all, folks!")
            break

        guess = incoming_message.content.upper()

        # ignore non-suffix, and cut it off
        if not guess.endswith(suffix):
            continue
        guess = guess[:-1]

        if guess in guesses:
            # CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS
            await incoming_message.add_reaction('\U0001f501')
            continue

        if guess not in ''.join(phrase):
            await incoming_message.add_reaction('\N{CROSS MARK}')
            continue

        if len(guess) == 1:
            # letter guess.
            # enumerate through the list of characters in the original phrase. if our current character matches,
            # go into the censored list of characters and replace it with the actual character.
            for phrase_index, phrase_character in enumerate(phrase):
                if phrase_character == guess:
                    phrase_base[phrase_index] = phrase_character
        else:
            # phrase guess.
            index_into_phrase = ''.join(phrase).index(guess)
            # insert into the place the guess.
            phrase_base[index_into_phrase:index_into_phrase+len(guess)] = list(guess)

        # delete the old game message and send the new one.
        await game_message.delete()
        game_message = await binded_channel.send(''.join(phrase_base))
        await incoming_message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

        # give points.
        points[incoming_message.author.id] = points.get(incoming_message.author.id, 0) + 1

        guesses.append(guess)

        if all(character != '-' for character in phrase_base):
            leaderboard = list(points.items())
            most_guesses = sorted(leaderboard, key=lambda e: e[1], reverse=True)[0]
            await binded_channel.send(
                "Game's over, hope you had fun!\n\n"
                f"<@{most_guesses[0]}> had the most guesses with **{most_guesses[1]} guesses.**"
            )
            break



class Hangman(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions: List[int] = []
        self.waiting_list: DefaultDict[int, Set[discord.User]] = defaultdict(set)
        self.waiting_lock = asyncio.Lock()
        self.session_lock = asyncio.Lock()

    async def add_to_waiting_list(self, channel: discord.TextChannel, user: discord.User):
        async with self.waiting_lock:
            self.waiting_list[channel.id].add(user)

    async def remove_from_waiting_list(self, channel: discord.TextChannel, user: discord.User):
        async with self.waiting_lock:
            self.waiting_list[channel.id].remove(user)

    @command(aliases=['start_hangman', 'hm'])
    @commands.guild_only()
    async def hangman_start(self, ctx: Context):
        """starts a game of hangman"""

        if ctx.channel.id in self.sessions:
            waiting_list = self.waiting_list.get(ctx.channel.id, [])
            if ctx.author in waiting_list:
                await ctx.send('You are already in the waiting list!')
                return
            await ctx.send('There is already a game here, but you have been added to a waiting list.')
            await self.add_to_waiting_list(ctx.channel, ctx.author)
            return

        async with self.session_lock:
            self.sessions.append(ctx.channel.id)

        await game(ctx, master=ctx.author, binded_channel=ctx.channel)

        # go through the waiting list.
        people_waiting = self.waiting_list.get(ctx.channel.id, set())
        for new_master in people_waiting.copy():
            await game(ctx, master=new_master, binded_channel=ctx.channel)
            await self.remove_from_waiting_list(ctx.channel, new_master)

        async with self.session_lock:
            self.sessions.remove(ctx.channel.id)


def setup(bot):
    bot.add_cog(Hangman(bot))
