import importlib
import logging
from pathlib import Path
from typing import Any, Union, List

import discord
from discord.ext import commands

from lifesaver.config import Config, Field
from .context import Context

INCLUDED_EXTENSIONS = ('lifesaver.bot.exts.admin', 'lifesaver.bot.exts.health', 'lifesaver.bot.exts.exec',
                       'lifesaver.bot.exts.errors')


class BotConfig(Config):
    #: The token of the bot.
    token = Field(str)

    #: The path from which to load extension files from.
    extensions_path = Field(str, default='./exts')

    #: Specifies whether to ignore bots when processing commands.
    ignore_bots = Field(bool, default=True)

    #: The command prefix to use.
    command_prefix = Field(Any)

    #: The bot's description.
    description = Field(str, default='A Discord bot.')

    #: Specifies whether to PM help or not.
    pm_help = Field(Any, default=None)

    #: Specifies whether mentions should count as prefixes, too.
    command_prefix_include_mentions = Field(bool, default=True)


def _convert_to_list(thing: Any) -> Union[Any, List[Any]]:
    return [thing] if not isinstance(thing, list) else thing


class BotBase(commands.bot.BotBase):
    """
    A :class:`commands.bot.BotBase` subclass that provides useful utilities.

    You should not be inheriting/using this class directly.
    """

    def __init__(self, cfg: BotConfig, **kwargs):
        #: The bot's :class:`BotConfig`.
        self.cfg = cfg

        super().__init__(
            # command prefix
            commands.when_mentioned_or(*_convert_to_list(cfg.command_prefix)) if cfg.command_prefix_include_mentions \
                else cfg.command_prefix,

            # other bot stuff
            description=self.cfg.description,
            pm_help=self.cfg.pm_help,

            **kwargs
        )

        #: The bot's logger.
        self.log = logging.getLogger(__name__)

        #: A list of extensions names to reload when calling Bot.load_all().
        self._extension_load_list = ()  # type: tuple

        #: A list of included extensions built into lifesaver to load.
        self._included_extensions = INCLUDED_EXTENSIONS  # type: tuple

    @classmethod
    def with_config(cls, config: str = 'config.yml'):
        """
        Creates a bot instance with a configuration file.

        Parameters
        ----------
        config : str
            The path to the configuration file.

        Returns
        -------
        The created bot instance.
        """
        return cls(BotConfig.load(config))

    def _rebuild_load_list(self):
        """Rebuilds the load list."""

        # Transforms a path like ``exts/hi.py`` to ``exts.hi``.
        def transform_path(path: Path) -> str:
            return str(path).replace('/', '.').replace('.py', '')

        # Build a list of extensions to load.
        exts_path = Path(self.cfg.extensions_path)
        paths = tuple(transform_path(x) for x in exts_path.glob('**/*.py') if x.name != '__init__.py')

        def _ext_filter(path: str):
            module = importlib.import_module(path)
            return hasattr(module, 'setup')

        paths = tuple(filter(_ext_filter, paths))

        self._extension_load_list = paths

    def load_all(self, *, unload_first: bool = False, exclude_default: bool = False):
        """
        Loads all extensions in the extensions load list. The load list is always rebuilt first when called.
        When done, ``load_all`` is dispatched with the value of ``unload_first``.

        Parameters
        ----------
        unload_first : bool
            Specifies whether to unload extensions before loading them.
        exclude_default : bool
            Specifies whether to leave out default extensions.
        """
        self._rebuild_load_list()

        load_list = self._extension_load_list if exclude_default \
            else (self._extension_load_list + self._included_extensions)

        for extension_name in load_list:
            if unload_first:
                self.unload_extension(extension_name)
            self.load_extension(extension_name)

        self.dispatch('load_all', unload_first)

    async def on_ready(self):
        self.log.info('Ready! %s (%d)', self.user, self.user.id)

    async def on_message(self, message: discord.Message):
        # Ignore bots if applicable.
        if self.cfg.ignore_bots and message.author.bot:
            return

        # Grab a context, then invoke it.
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        # handled by errors.py
        pass


class Bot(BotBase, discord.Client):
    """A bot class that provides useful utilities."""

    def run(self):
        super().run(self.cfg.token)


class Selfbot(BotBase, discord.Client):
    """A selfbot class that provides useful utilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, self_bot=True, **kwargs)

    def run(self):
        super().run(self.cfg.token, bot=False)


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    """An automatically sharded bot class that provides useful utilities."""

    def run(self):
        super().run(self.cfg.token)
