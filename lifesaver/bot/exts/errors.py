import time
import traceback
import uuid

import datetime
from collections import OrderedDict

import discord
from discord.ext import commands
from discord.ext.commands import group

from lifesaver.bot import Cog
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.utils import codeblock


def get_traceback(exc: Exception, *, limit=7) -> str:
    return ''.join(traceback.format_exception(
        type(exc), exc, exc.__traceback__, limit=limit
    ))


class Errors(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insects = AsyncJSONStorage('./insects.json')

    async def _save_insect(self, error: Exception):
        # grab insect list
        insects = self.insects.get('insects') or []

        # append to array
        insect_id = str(uuid.uuid4())
        insects.append(
            {
                'id': insect_id,
                'creation_time': time.time(),
                'traceback': get_traceback(error)
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
    async def throw(self, ctx, *, message):
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

            prefix, append_message = info
            return await ctx.send(prefix + (f': {error}' if append_message else ''))

        if isinstance(error, commands.CommandInvokeError):
            insect_id = await self._save_insect(error)
            await ctx.send(f'A fatal error has occurred while running that command. Insect ID: `{insect_id}`')
            self.log.error('Fatal error. ' + get_traceback(error))


def setup(bot):
    bot.add_cog(Errors(bot))
