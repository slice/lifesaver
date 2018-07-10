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
import time
import uuid
from collections import OrderedDict

import discord
from discord.ext import commands
from lifesaver.bot import Cog, Context, group, errors
from lifesaver.bot.command import SubcommandInvocationRequired
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.utils import codeblock, format_traceback


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
            'traceback': format_traceback(error, hide_paths=True)
        })

        await self.insects.put('insects', insects)
        return insect_id

    @group(hidden=True, hollow=True)
    @commands.is_owner()
    async def errors(self, ctx: Context):
        """Manages errors."""

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

        error_handlers = OrderedDict([
            (commands.BotMissingPermissions, ('Whoops!', True)),
            (commands.MissingPermissions, ('Whoops!', True)),
            (commands.NoPrivateMessage, ("You can't do that in a DM.", False)),
            (commands.NotOwner, ("Only the owner of this bot can do that.", False)),
            (commands.DisabledCommand, ('That command has been disabled.', False)),
            (commands.UserInputError, ('User input error', True)),
            (commands.CheckFailure, ('Permissions error', True)),
            (SubcommandInvocationRequired,
             ('You need to specify a valid subcommand to run. For help, run `{prefix}help {command}`.', False)
             ),
        ])

        ignored_errors = getattr(ctx.bot, 'ignored_errors')
        if ignored_errors is not None:
            try:
                for ignored_error in ignored_errors:
                    del error_handlers[ignored_error]
            except KeyError:
                pass

        if isinstance(error, errors.MessageError):
            await ctx.send(error.message)
            return

        if isinstance(error, commands.BadArgument):
            if hasattr(error, '__cause__') and 'failed for parameter' in str(error):
                self.log.error('Generic check error. ' + format_traceback(error.__cause__))
            await ctx.send(f'Bad argument. {error}')
            return

        for error_type, (prefix, prepend_message) in error_handlers.items():
            if not isinstance(error, error_type):
                continue

            prefix_post = prefix.format(prefix=ctx.prefix, command=ctx.command.qualified_name)
            await ctx.send(prefix_post + (f': {error}' if prepend_message else ''))
            return

        if isinstance(error, commands.CommandInvokeError):
            insect_id = await self._save_insect(error)
            await ctx.send(f'A fatal error has occurred. \N{BUG} `{insect_id}`')
            self.log.error('Fatal error. ' + format_traceback(error))


def setup(bot):
    bot.add_cog(Errors(bot))
