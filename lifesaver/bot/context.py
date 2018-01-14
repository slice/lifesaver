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

import discord
from discord.ext import commands


class Context(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._paginator = commands.Paginator()

    def __iadd__(self, line: str) -> 'Context':
        self._paginator.add_line(line)
        return self

    async def send_pages(self, *, prefix: str = '```', suffix: str = '```'):
        self._paginator.prefix = prefix
        self._paginator.suffix = suffix
        for page in self._paginator.pages:
            await self.send(page)

    async def ok(self, emoji='\N{OK HAND SIGN}'):
        """Makes the bot respond with an emoji in acknowledgement to an action performed by the user."""
        actions = [self.message.add_reaction, self.send, self.author.send]

        for action in actions:
            try:
                await action(emoji)
                break
            except discord.HTTPException:
                pass
