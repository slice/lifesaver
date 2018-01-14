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

import datetime
import os
import pathlib
import time
import traceback
import uuid
from collections import OrderedDict

import discord
from discord.ext import commands
from discord.ext.commands import group

from lifesaver.bot import Cog, Context
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.utils import codeblock


def get_traceback(exc: Exception, *, limit: int = 7, hide_paths: bool = False) -> str:
    formatted = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__, limit=limit))

    if hide_paths:
        # censor cwd
        formatted = formatted.replace(os.getcwd(), '/...')

        # hide packages directory
        packages_dir = str(pathlib.Path(discord.__file__).parent.parent.resolve())
        formatted = formatted.replace(packages_dir, '/packages')

    return formatted


class Errors(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insects = AsyncJSONStorage('./insects.json')

    async def _save_insect(self, error: Exception):
        insects = self.insects.get('insects') or []

        insect_id = str(uuid.uuid4())
        insects.append({
            'id': insect_id,
            'creation_time': time.time(),
            'traceback': get_traceback(error, hide_paths=True)
        })

        await self.insects.put('insects', insects)
        return insect_id

    @group(hidden=True)
    @commands.is_owner()
    async def errors(self, ctx: Context):
        """Manages errors."""
        pass

    @errors.command(aliases=['show', 'info'])
    async def view(self, ctx: Context, insect_id):
        """Views an error by insect ID."""
        all_insects = self.insects.get('insects') or []
        insect = discord.utils.find(lambda insect: insect['id'] == insect_id, all_insects)

        if not insect:
            return await ctx.send("An insect with that ID wasn't found.")

        created = datetime.datetime.fromtimestamp(insect['creation_time'])
        ago = str(datetime.datetime.utcnow() - created)

        embed = discord.Embed(title=f'Insect {insect_id}')
        embed.add_field(name='Created', value=f'{created} ({ago} ago)', inline=False)
        await ctx.send(codeblock(insect['traceback'], lang='py'), embed=embed)

    @errors.command(hidden=True)
    async def throw(self, ctx: Context, *, message='Error!'):
        """Throws an intentional error. Used for debugging."""
        raise RuntimeError(f'Intentional error: {message}')

    async def on_command_error(self, ctx: Context, error: Exception):
        """Default error handler."""

        # yapf: disable
        error_handlers = OrderedDict([
            (commands.BotMissingPermissions, ('Whoops!', True)),
            (commands.MissingPermissions, ('Whoops!', True)),
            (commands.NoPrivateMessage, ("You can't do that in a DM.", False)),
            (commands.NotOwner, ("Only the owner of this bot can do that.", False)),
            (commands.DisabledCommand, ('That command has been disabled.', False)),
            (commands.UserInputError, ('User input error', True)),
            (commands.CheckFailure, ('Permissions error', True))
        ])
        # yapf: enable

        for error_type, info in error_handlers.items():
            if not isinstance(error, error_type):
                continue

            prefix, prepend_message = info
            return await ctx.send(prefix + (f': {error}' if prepend_message else ''))

        if isinstance(error, commands.CommandInvokeError):
            insect_id = await self._save_insect(error)
            await ctx.send('A fatal error has occurred while running that command. ' +
                           f'Please report this error ID to the bot owner: `{insect_id}` ' + 'Thanks!')
            self.log.error('Fatal error. ' + get_traceback(error))


def setup(bot):
    bot.add_cog(Errors(bot))
