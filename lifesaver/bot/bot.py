from pathlib import Path

import discord
from discord.ext import commands

from lifesaver.config import Config, Field
from .context import LifesaverContext

INCLUDED_EXTENSIONS = (
    'lifesaver.bot.exts.admin',
    'lifesaver.bot.exts.health',
    'lifesaver.bot.exts.exec'
)


class BotConfig(Config):
    #: The token of the bot.
    token = Field(str)

    #: The path from which to load extension files from.
    extensions_path = Field(str, default='./exts')

    #: Specifies whether to ignore bots when processing commands.
    ignore_bots = Field(bool, default=True)

    #: The command prefix to use.
    command_prefix = Field(str)


class BotBase(commands.bot.BotBase):
    """
    A :class:`commands.bot.BotBase` subclass that provides useful utilities.

    You should not be inheriting/using this class directly.
    """
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg.command_prefix, **kwargs)

        #: The bot's :class:`BotConfig`.
        self.cfg = cfg

        #: A list of extensions names to reload when calling Bot.load_all().
        self._extension_load_list = ()  # type: tuple

        #: A list of included extensions built into lifesaver to load.
        self._included_extensions = INCLUDED_EXTENSIONS  # type: tuple

    @classmethod
    def with_config(cls, config='config.yml'):
        """
        Creates a bot instance with a configuration file.

        :param config: The path to the configuration file.
        :type config: str
        :return: The bot instance.
        """
        return cls(BotConfig.load(config))

    def _rebuild_load_list(self):
        """Rebuilds the load list."""

        # Transforms a path like ``exts/hi.py`` to ``exts.hi``.
        def transform_path(path):
            return str(path).replace('/', '.').replace('.py', '')

        # Build a list of extensions to load.
        exts_path = Path(self.cfg.extensions_path)
        paths = tuple(transform_path(x) for x in exts_path.glob('**/*.py') if x.name != '__init__.py')

        self._extension_load_list = paths

    def load_all(self, *, unload_first: bool=False, exclude_default: bool=False):
        """
        Loads all extensions in the extensions path.

        :param unload_first: Specifies whether to unload an extension before loading it.
        :param exclude_default: Specifies whether to leave out default extensions.
        """
        self._rebuild_load_list()

        load_list = self._extension_load_list if exclude_default\
            else (self._extension_load_list + self._included_extensions)

        for extension_name in load_list:
            if unload_first:
                self.unload_extension(extension_name)
            self.load_extension(extension_name)

        self.dispatch('load_all', unload_first)

    async def on_message(self, message: discord.Message):
        # Ignore bots if applicable.
        if self.cfg.ignore_bots and message.author.bot:
            return

        ctx = await self.get_context(message, cls=LifesaverContext)
        await self.invoke(ctx)


class Bot(BotBase, discord.Client):
    """
    A bot class that provides useful utilities.
    """
    def run(self):
        super().run(self.cfg.token)


class Selfbot(BotBase, discord.Client):
    """
    A selfbot class that provides useful utilities.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, self_bot=True, **kwargs)

    def run(self):
        super().run(self.cfg.token, bot=False)


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    """
    An automatically sharded bot class that provides useful utilities.
    """
    def run(self):
        super().run(self.cfg.token)
