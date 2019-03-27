# encoding: utf-8

import logging
from pathlib import Path
from typing import Union

import discord
from discord.ext import commands

from lifesaver.poller import Poller, PollerPlug
from lifesaver.utils import dot_access
from lifesaver.load_list import LoadList

from .config import BotConfig
from .context import Context

INCLUDED_EXTENSIONS = [
    'jishaku',
    'lifesaver.bot.exts.health',
    'lifesaver.bot.exts.errors',
]


def compute_command_prefix(cfg: BotConfig):
    prefix = cfg.command_prefix

    if cfg.command_prefix_include_mentions:
        if prefix is None:
            return commands.when_mentioned
        else:
            if isinstance(prefix, str):
                return commands.when_mentioned_or(prefix)
            elif isinstance(prefix, list):
                return commands.when_mentioned_or(*prefix)
    else:
        return prefix


class BotBase(commands.bot.BotBase):
    def __init__(self, cfg: BotConfig, **kwargs) -> None:
        #: The bot's :class:`BotConfig`.
        self.config = cfg

        command_prefix = kwargs.pop('command_prefix', compute_command_prefix(cfg))
        description = kwargs.pop('description', self.config.description)
        help_command = kwargs.pop('help_command', commands.DefaultHelpCommand(dm_help=cfg.dm_help))

        super().__init__(
            command_prefix=command_prefix,
            description=description,
            help_command=help_command,
            **kwargs,
        )

        #: The bot's :class:`Context` subclass to use when invoking commands.
        #: Falls back to :class:`Context`.
        self.context_cls = kwargs.get('context_cls', Context)

        if not issubclass(self.context_cls, Context):
            raise TypeError(f'{self.context_cls} is not a lifesaver Context subclass')

        #: The Postgres pool connection.
        self.pg_pool = None

        #: The bot's logger.
        self.log = logging.getLogger(__name__)

        #: A list of extensions names to reload when calling :meth:`load_all`.
        self.load_list = LoadList()

        #: A list of included extensions built into lifesaver to load.
        self._included_extensions = INCLUDED_EXTENSIONS  # type: list

        self._hot_task = None
        self._hot_plug = None

    def emoji(self, accessor: str, *, stringify: bool = False) -> Union[str, discord.Emoji]:
        """Return an emoji as referenced by the global emoji table.

        The first argument accesses the :attr:`BotConfig.emojis` dict using
        "dot access syntax" (e.g. ``generic.ok`` does ``['generic']['ok']``).

        Both Unicode codepoints and custom emoji IDs are supported. If a custom
        emoji ID is used, :meth:`discord.Client.get_emoji` is called to
        retrieve the :class:`discord.Emoji`.
        """
        emoji_id = dot_access(self.config.emojis, accessor)

        if isinstance(emoji_id, int):
            emoji = self.get_emoji(emoji_id)
        else:
            emoji = emoji_id

        if stringify:
            return str(emoji)
        else:
            return emoji

    def tick(self, variant: bool = True) -> Union[str, discord.Emoji]:
        """Return a tick emoji.

        Uses ``generic.yes`` and ``generic.no`` from the global emoji table.
        """
        if variant:
            return self.emoji('generic.yes')
        else:
            return self.emoji('generic.no')

    async def _hot_reload(self):
        poller = Poller(path=self.config.extensions_path, polling_interval=0.1)
        self.log.debug('created poller: %s', poller)

        async for event in poller:
            self._hot_plug.handle(event)
            self._rebuild_load_list()

    async def _postgres_connect(self):
        try:
            import asyncpg
        except ImportError:
            raise RuntimeError('Cannot connect to Postgres, asyncpg is not installed')

        self.log.debug('creating a postgres pool')

        self.pg_pool = await asyncpg.create_pool(
            dsn=self.config.postgres['dsn'],
        )

        self.log.debug('created postgres pool')

    def _rebuild_load_list(self):
        self.load_list.build(Path(self.config.extensions_path))

    def load_all(self, *, reload: bool = False, exclude_default: bool = False):
        """Load all extensions in the load list.

        The load list is always rebuilt first when called.
        When done, the ``load_all`` event is dispatched with the value of ``reload``.

        Parameters
        ----------
        reload
            Reload extensions instead of loading them. Uses
            :meth:`discord.ext.commands.Bot.reload_extension`.
        exclude_default
            Exclude default extensions from being loaded.
        """
        self._rebuild_load_list()

        if exclude_default:
            load_list = self.load_list
        else:
            load_list = self.load_list + self._included_extensions

        for extension_name in load_list:
            if reload:
                self.reload_extension(extension_name)
            else:
                self.load_extension(extension_name)

        self.dispatch('load_all', reload)

    async def on_ready(self):
        self.log.info('Ready! %s (%d)', self.user, self.user.id)

        if self.config.postgres:
            await self._postgres_connect()

        if self.config.hot_reload:
            self.log.debug('Setting up hot reload.')
            self._hot_plug = PollerPlug(self)
            self._hot_task = self.loop.create_task(self._hot_reload())

    async def on_message(self, message: discord.Message):
        """The handler that handles incoming messages from Discord.

        This event automatically waits for the bot to be ready before processing
        commands. Bots are ignored according to :attr:`BotConfig.ignore_bots`
        and the context class used for commands is determined by
        :attr:`context_cls`.
        """
        await self.wait_until_ready()

        # Ignore bots if applicable.
        if self.config.ignore_bots and message.author.bot:
            return

        # Grab a context, then invoke it.
        ctx = await self.get_context(message, cls=self.context_cls)
        await self.invoke(ctx)

    async def on_command_error(self, ctx: Context, exception: Exception):
        """The handler that handles command errors.

        This is a no-op. The Errors cog handles errors for us.
        """
        # Handled by errors.py.
        pass


class Bot(BotBase, discord.Client):
    def run(self):
        super().run(self.config.token)


class Selfbot(BotBase, discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, self_bot=True, **kwargs)

    def run(self):
        super().run(self.config.token, bot=False)


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    def run(self):
        super().run(self.config.token)
