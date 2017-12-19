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

from lifesaver.bot import Cog
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.utils import codeblock


def get_traceback(exc: Exception, *, limit=7, hide_paths=False) -> str:
    formatted = ''.join(traceback.format_exception(
        type(exc), exc, exc.__traceback__, limit=limit
    ))

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
        insects.append(
            {
                'id': insect_id,
                'creation_time': time.time(),
                'traceback': get_traceback(error, hide_paths=True)
            }
        )

        await self.insects.put('insects', insects)
        return insect_id

    @group(hidden=True)
    @commands.is_owner()
    async def errors(self, ctx):
        """Manages errors."""
        pass

    @errors.command(aliases=['show', 'info'])
    async def view(self, ctx, insect_id: str):
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

    @errors.command()
    async def throw(self, ctx, *, message='Error!'):
        """Throws an intentional error. Used for debugging."""
        raise RuntimeError(f'Intentional error: {message}')

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Default error handler."""

        error_handlers = OrderedDict([
            (commands.BotMissingPermissions, ('Whoops!', True)),
            (commands.MissingPermissions, ('Whoops!', True)),
            (commands.NoPrivateMessage, ("You can't do that in a DM.", False)),
            (commands.NotOwner, ("Only the owner of this bot can do that.", False)),
            (commands.DisabledCommand, ('That command has been disabled.', False)),
            (commands.UserInputError, ('User input error', True)),
            (commands.CheckFailure, ('Permissions error', True))
        ])

        for error_type, info in error_handlers.items():
            if not isinstance(error, error_type):
                continue

            prefix, prepend_message = info
            return await ctx.send(prefix + (f': {error}' if prepend_message else ''))

        if isinstance(error, commands.CommandInvokeError):
            insect_id = await self._save_insect(error)
            await ctx.send(
                'A fatal error has occurred while running that command. ' +
                f'Please report this error ID to the bot owner: `{insect_id}` ' +
                'Thanks!'
            )
            self.log.error('Fatal error. ' + get_traceback(error))


def setup(bot):
    bot.add_cog(Errors(bot))
