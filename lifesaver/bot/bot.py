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
import logging
from pathlib import Path
from typing import List, Union, Dict, Any

import discord
from discord.ext import commands
from lifesaver.config import Config
from lifesaver.poller import Poller, PollerPlug
from lifesaver.utils import dot_access
from lifesaver.load_list import LoadList

from .context import Context

INCLUDED_EXTENSIONS = [
    'lifesaver.bot.exts.admin',
    'lifesaver.bot.exts.health',
    'lifesaver.bot.exts.exec',
    'lifesaver.bot.exts.errors',
]


class BotConfig(Config):
    #: The token of the bot.
    token: str

    #: The path from which to load extension files from.
    extensions_path: str = './exts'

    #: The path for cog-specific configuration files
    cog_config_path: str = './config'

    #: Ignores bots when processing commands.
    ignore_bots: bool = True

    #: The command prefix to use.
    command_prefix: Union[List[str], str] = '!'

    #: The bot's description.
    description: str = 'A Discord bot.'

    #: PMs help messages.
    pm_help: Union[bool, None] = None

    #: Includes mentions as valid prefixes.
    command_prefix_include_mentions: bool = True

    #: Activates the hot reloader.
    hot_reload: bool = False

    #: Bot emojis.
    emojis: Dict[str, Union[str, int]]

    #: Postgres access credentials.
    postgres: Dict[str, Any] = None


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

        super().__init__(
            command_prefix=compute_command_prefix(cfg),
            description=self.config.description,
            pm_help=self.config.pm_help,

            **kwargs,
        )

        #: The bot's :class:`Context` subclass to use when invoking commands.
        self.context_cls = kwargs.get('context_cls', Context)

        if not issubclass(self.context_cls, Context):
            raise TypeError(f'{self.context_cls} is not a lifesaver Context subclass')

        #: The Postgres pool connection.
        self.pg_pool = None

        #: The bot's logger.
        self.log = logging.getLogger(__name__)

        #: A list of extensions names to reload when calling Bot.load_all().
        self.load_list = LoadList()

        #: A list of included extensions built into lifesaver to load.
        self._included_extensions = INCLUDED_EXTENSIONS  # type: list

        self._hot_task = None
        self._hot_plug = None

    async def close(self):
        self.log.info('Closing.')
        await super().close()

    def emoji(self, accessor: str, *, stringify: bool = False) -> Union[str, discord.Emoji]:
        """Return a bot emoji by name."""
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
        """Return a tick bot emoji."""
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

    def load_all(self, *, unload_first: bool = False, exclude_default: bool = False):
        """Load all extensions in the load list.
        The load list is always rebuilt first when called.
        When done, the ``load_all`` event is dispatched with the value of ``unload_first``.

        Parameters
        ----------
        unload_first
            Unload extensions before loading them (makes the call function as a reload).
        exclude_default
            Exclude default extensions from being loaded.
        """
        self._rebuild_load_list()

        if exclude_default:
            load_list = self.load_list
        else:
            load_list = self.load_list + self._included_extensions

        for extension_name in load_list:
            if unload_first:
                self.unload_extension(extension_name)
            self.load_extension(extension_name)

        self.dispatch('load_all', unload_first)

    async def on_ready(self):
        self.log.info('Ready! %s (%d)', self.user, self.user.id)

        if self.config.postgres:
            await self._postgres_connect()

        if self.config.hot_reload:
            self.log.debug('Setting up hot reload.')
            self._hot_plug = PollerPlug(self)
            self._hot_task = self.loop.create_task(self._hot_reload())

    async def on_message(self, message: discord.Message):
        await self.wait_until_ready()

        # Ignore bots if applicable.
        if self.config.ignore_bots and message.author.bot:
            return

        # Grab a context, then invoke it.
        ctx = await self.get_context(message, cls=self.context_cls)
        await self.invoke(ctx)

    async def on_command_error(self, ctx: Context, exception: Exception):
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
