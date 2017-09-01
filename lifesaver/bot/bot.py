from pathlib import Path

import discord
from discord.ext import commands

from .context import LifesaverContext

INCLUDED_EXTENSIONS = (
    'lifesaver.bot.exts.admin',
    'lifesaver.bot.exts.health'
)


class BotBase(commands.bot.BotBase):
    """
    A ``commands.bot.BotBase`` subclass that provides useful utilities.

    You should not be inheriting/using this class directly.
    """
    def __init__(self, *args, extensions_path: str, ignore_bots: bool=True, **kwargs):
        super().__init__(*args, **kwargs)

        #: The path from which to load extensions from, relative to the current directory.
        self.extensions_path = extensions_path

        #: Specifies whether to ignore bots or not.
        self.ignore_bots = ignore_bots

        #: A list of extensions names to reload when calling Bot.load_all().
        self._extension_load_list = []

    def _rebuild_load_list(self):
        """Rebuilds the load list."""

        # Transforms a path like ``exts/hi.py`` to ``exts.hi``.
        def transform_path(path):
            return str(path).replace('/', '.').replace('.py', '')

        # Build a list of extensions to load.
        exts_path = Path(self.extensions_path)
        paths = tuple(transform_path(x) for x in exts_path.glob('**/*.py') if x.name != '__init__.py')

        self._extension_load_list = paths + INCLUDED_EXTENSIONS

    def load_all(self, *, unload_first: bool=False, exclude_default: bool=False):
        """
        Loads all extensions in the extensions path.

        :param unload_first: Specifies whether to unload an extension before loading it.
        """
        self._rebuild_load_list()

        for extension_name in self._extension_load_list:
            if unload_first:
                self.unload_extension(extension_name)
            self.load_extension(extension_name)

        self.dispatch('lf_bot_load_all', unload_first)

    async def on_message(self, message: discord.Message):
        # Ignore bots if applicable.
        if self.ignore_bots and message.author.bot:
            return

        ctx = await self.get_context(message, cls=LifesaverContext)
        await self.invoke(ctx)


class Bot(BotBase, discord.Client):
    """
    A bot class that provides useful utilities.
    """
    pass


class Selfbot(BotBase, discord.Client):
    """
    A selfbot class that provides useful utilities.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, self_bot=True, **kwargs)


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    """
    An automatically sharded bot class that provides useful utilities.
    """
    pass
