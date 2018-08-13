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
from typing import Any, List, Optional

import discord
from discord.ext import commands
from lifesaver import utils

SCRUBBING = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere',
}


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._paginator = commands.Paginator()

    def __iadd__(self, line: str) -> 'Context':
        self._paginator.add_line(line)
        return self

    async def send(self, content: str = None, *args, scrub: bool = True, **kwargs) -> discord.Message:
        if content and scrub:
            for from_, to in SCRUBBING.items():
                content = content.replace(from_, to)
        return await super().send(content, *args, **kwargs)

    async def confirm(self, title: str, message: str = None, *, color: discord.Color = discord.Color.red(),
                      delete_after: bool = False, cancellation_message: Optional[str] = None) -> bool:
        """
        Waits for confirmation by the user.

        Parameters
        ----------
        title : str
            The title of the confirmation prompt.
        message : str
            The message (description) of the confirmation prompt.
        color : :class:`discord.Color`
            The color of the embed.
        delete_after : bool
            Specifies whether to delete the confirmation after a choice has been picked.
        cancellation_message : Optional[str]
            A message to send after cancelling.

        Returns
        -------
        bool
            Whether the user confirmed or not.
        """

        embed = discord.Embed(title=title, description=message, color=color)
        message: discord.Message = await self.send(embed=embed)

        reactions = {'\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'}
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return user == self.author and reaction.message.id == message.id and reaction.emoji in reactions

        reaction, _ = await self.bot.wait_for('reaction_add', check=check)
        if delete_after:
            await message.delete()
        confirmed = reaction.emoji == '\N{WHITE HEAVY CHECK MARK}'
        if not confirmed and cancellation_message:
            await self.send(cancellation_message)
        return confirmed

    async def wait_for_response(self) -> discord.Message:
        """
        Waits for a message response from the message author, then returns the
        new message.

        The message we are waiting for will only be accepted if it was sent by
        the original command invoker, and it was sent in the same channel as
        the command message.

        Returns
        -------
        discord.Message
            The sent message.
        """

        def check(m: discord.Message):
            if isinstance(m.channel, discord.DMChannel):
                # accept any message, because we are in a dm
                return True
            return m.channel.id == self.channel.id and m.author == self.author

        return await self.bot.wait_for('message', check=check)

    async def pick_from_list(self, choices: List[Any], *, delete_after_choice: bool = False, tries: int = 3) -> Any:
        """
        Shows the user a list of items to pick from, and returns the picked item.

        Parameters
        ----------
        choices : list of any
            The list of choices.
        delete_after_choice : bool
            Specifies whether to delete the message prompt after the user has picked.
        tries : int
            The amount of tries to give to the user.
        """
        # format list of stuff
        choices_list = utils.format_list(choices)

        # send list of stuff
        choices_message = await self.send('Pick one, or send `cancel`.\n\n' + choices_list)
        remaining_tries = tries
        picked = None

        while True:
            if remaining_tries <= 0:
                await self.send('You ran out of tries, I give up!')
                return None

            # wait for a message
            msg = await self.wait_for_response()

            # user wants to cancel?
            if msg.content == 'cancel':
                await self.send('Canceled selection.')
                break

            try:
                chosen_index = int(msg.content) - 1
            except ValueError:
                # they didn't enter a valid number
                await self.send('Invalid number. Send the number of the item you want.')
                remaining_tries -= 1
                continue

            if chosen_index < 0 or chosen_index > len(choices) - 1:
                # out of range
                await self.send('Invalid choice. Send the number of the item you want.')
                remaining_tries -= 1
            else:
                # they chose correctly
                picked = choices[chosen_index]
                if delete_after_choice:
                    await choices_message.delete()
                    await msg.delete()
                break

        return picked

    def new_paginator(self, *args, **kwargs):
        self._paginator = commands.Paginator(*args, **kwargs)

    async def send_pages(self):
        for page in self._paginator.pages:
            await self.send(page)

    async def ok(self, emoji: str = '\N{OK HAND SIGN}'):
        """
        Makes the bot respond with an emoji in acknowledgement to an action performed by the user.

        Parameters
        ----------
        emoji : str
            The emoji to react with.
        """
        actions = [self.message.add_reaction, self.send, self.author.send]

        for action in actions:
            try:
                await action(emoji)
                break
            except discord.HTTPException:
                pass
