from typing import List

import asyncio
import re

import discord
from discord.ext import commands

from lifesaver.bot import Cog, command, Context


class Hangman(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = []
        self.session_lock = asyncio.Lock()

    @command(aliases=['start_hangman', 'hm'])
    @commands.guild_only()
    async def hangman_start(self, ctx: Context):
        """starts a game of hangman"""
        game_master: discord.Member = ctx.author
        binded_channel: discord.TextChannel = ctx.channel
        phrase: List[str] = None
        points = {}
        guesses = []

        if ctx.channel.id in self.sessions:
            await ctx.send('There is already a game here. You can start one in another channel.')
            return

        async with self.session_lock:
            self.sessions.append(binded_channel.id)

        try:
            status_update = await binded_channel.send(
                f'Waiting for the master ({game_master}) to start the game...'
            )
        except discord.HTTPException:
            # cannot send in binded channel
            return

        async def status_aborted():
            await status_update.edit(content=f'Bleh, {game_master.display_name} failed to start the game. Shame.')
            async with self.session_lock:
                self.sessions.remove(binded_channel.id)

        try:
            await game_master.send('Send me your phrase!')

            # wait for the dm-ed phrase from the game master.
            phrase_message = await ctx.bot.wait_for(
                'message',
                check=lambda m: not m.guild and m.author == game_master
            )
            phrase = list(phrase_message.content.upper())

            if len(phrase) > 140:
                await game_master.send('That phrase is too long, 140 letters maximum.')
                await status_aborted()
                return

            if '-' in phrase:
                await game_master.send('Phrases cannot contain `-`s. Sorry!')
                await status_aborted()
                return

            if not phrase_message.content:
                await game_master.send('Uhh, you need to send some text.')
                await status_aborted()
                return

            await game_master.send(
                f'Okay, game started in {binded_channel.mention}! '
                'Send `cancel!` at any time in that channel to stop the game, if you want.'
            )
        except discord.HTTPException:
            await ctx.send("I can't DM you, game aborted.")
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

            if incoming_message.author == game_master:
                if incoming_message.content == 'cancel!':
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

        async with self.session_lock:
            self.sessions.remove(binded_channel.id)


def setup(bot):
    bot.add_cog(Hangman(bot))
