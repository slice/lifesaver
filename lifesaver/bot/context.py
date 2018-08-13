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
from typing import Any, List

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

    @property
    def can_send_embeds(self) -> bool:
        """Return whether the bot can send embeds in this context."""
        if self.guild is None:
            return True

        channel = self.channel
        guild = self.guild

        perms = channel.permissions_for(guild.me)
        return perms.embed_links

    async def send(self, content: str = None, *args, scrub: bool = True, **kwargs) -> discord.Message:
        if content and scrub:
            for from_, to in SCRUBBING.items():
                content = content.replace(from_, to)
        return await super().send(content, *args, **kwargs)

    async def confirm(
        self,
        title: str,
        message: str = None,
        *,
        color: discord.Color = discord.Color.red(),
        delete_after: bool = False,
        cancellation_message: str = None
    ) -> bool:
        """
        Wait for confirmation by the user.

        Parameters
        ----------
        title
            The title of the confirmation prompt.
        message
            The message (description) of the confirmation prompt.
        color
            The color of the embed.
        delete_after
            Deletes the confirmation after a choice has been picked.
        cancellation_message
            A message to send after cancelling.

        Returns
        -------
        bool
            Whether the user confirmed or not.
        """

        embed = discord.Embed(title=title, description=message, color=color)
        msg: discord.Message = await self.send(embed=embed)

        reactions = {'\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'}
        for emoji in reactions:
            await msg.add_reaction(emoji)

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return all([
                user == self.author,
                reaction.message.id == msg.id,
                reaction.emoji in reactions,
            ])

        reaction, _ = await self.bot.wait_for('reaction_add', check=check)

        if delete_after:
            await msg.delete()

        confirmed = reaction.emoji == '\N{WHITE HEAVY CHECK MARK}'
        if not confirmed and cancellation_message:
            await self.send(cancellation_message)

        return confirmed

    async def wait_for_response(self) -> discord.Message:
        """
        Wait for a message response from the message author, then returns it.

        The message we are waiting for will only be accepted if it was sent by
        the original command invoker, and if it was sent in the same channel as
        the command message.

        Returns
        -------
        discord.Message
            The sent message.
        """

        def check(m: discord.Message):
            if isinstance(m.channel, discord.DMChannel):
                # Accept any message, because we are in a DM.
                return True
            return m.channel.id == self.channel.id and m.author == self.author

        return await self.bot.wait_for('message', check=check)

    async def pick_from_list(self, choices: List[Any], *, delete_after_choice: bool = False, tries: int = 3) -> Any:
        """
        Show the user a list of items to pick from, and returns the picked item.

        Parameters
        ----------
        choices
            The list of choices.
        delete_after_choice
            Deletes the message prompt after the user has picked.
        tries
            The amount of tries to grant the user.
        """
        choices_list = utils.format_list(choices)

        choices_message = await self.send('Pick one, or send `cancel`.\n\n' + choices_list)
        remaining_tries = tries
        picked = None

        while True:
            if remaining_tries <= 0:
                await self.send('You ran out of tries, I give up!')
                return None

            msg = await self.wait_for_response()

            if msg.content == 'cancel':
                await self.send('Canceled selection.')
                break

            try:
                chosen_index = int(msg.content) - 1
            except ValueError:
                await self.send('Invalid number. Send the number of the item you want.')
                remaining_tries -= 1
                continue

            if chosen_index < 0 or chosen_index > len(choices) - 1:
                await self.send('Invalid choice. Send the number of the item you want.')
                remaining_tries -= 1
            else:
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
        Respond with an emoji in acknowledgement to an action performed by the user.

        Parameters
        ----------
        emoji
            The emoji to react with.
        """
        actions = [self.message.add_reaction, self.send, self.author.send]

        for action in actions:
            try:
                await action(emoji)
                break
            except discord.HTTPException:
                pass
