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
import asyncio
import datetime
import importlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Union

import discord
from discord.ext import commands
from lifesaver.config import Config, Field
from lifesaver.fs import Poller
from lifesaver.utils import format_traceback

from .context import Context

INCLUDED_EXTENSIONS = ['lifesaver.bot.exts.admin', 'lifesaver.bot.exts.health', 'lifesaver.bot.exts.exec',
                       'lifesaver.bot.exts.errors']


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

    #: Specifies whether to automatically reload extensions upon changing them.
    hot_reload = Field(bool, default=False)


def _convert_to_list(thing: Any) -> Union[Any, List[Any]]:
    return [thing] if not isinstance(thing, list) else thing


def exception_handler(_loop: asyncio.AbstractEventLoop, ctx):
    now = datetime.datetime.now().strftime('[%m/%d/%Y %H:%M:%S]')
    formatted_error = '\n' + format_traceback(ctx["exception"]) if 'exception' in ctx else ''
    message = f'{now} asyncio exception handler triggered: {ctx["message"]}{formatted_error}'
    print(message, file=sys.stderr)


def transform_path(path: Union[Path, str]) -> str:
    """Transforms a path like ``exts/hi.py`` to ``exts.hi``."""
    return str(path).replace('/', '.').replace('.py', '')


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

        # Hot reload stuff.
        self._hot_task = None

        self._loop_setup()

    async def close(self):
        self.log.info('Closing.')
        await super().close()

    async def _hot_reload(self):
        poller = Poller(path=self.cfg.extensions_path, polling_interval=0.1)
        self.log.debug('created poller: %s', poller)
        async for event in poller:
            self.handle_hot_event(event)

    def handle_hot_event(self, event: Dict[str, Set[str]]):
        def resolve_module(filename):
            return transform_path(Path(self.cfg.extensions_path) / filename)

        def attempt_load(module):
            try:
                self.load_extension(module)
            except Exception:
                self.log.exception('Failed to hot-load %s, ignoring:', module)

        for created_file in event['created']:
            module = resolve_module(created_file)
            self.log.debug('hot: attempting to hot-load new extension %s', module)
            attempt_load(module)
        for deleted_file in event['deleted']:
            module = resolve_module(deleted_file)
            if module in self.extensions:
                self.log.debug('hot: unloading %s', module)
                self.unload_extension(module)
            else:
                self.log.debug('hot: not unloading %s, not loaded', module)
            try:
                del sys.modules[module]
            except KeyError:
                pass
        for updated_file in event['updated']:
            module = resolve_module(updated_file)
            self.log.debug('hot: reloading %s', module)
            if module in self.extensions:
                self.unload_extension(module)
            try:
                del sys.modules[module]
            except KeyError:
                pass
            attempt_load(module)

        self._rebuild_load_list()

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

        # Build a list of extensions to load.
        exts_path = Path(self.cfg.extensions_path)
        paths = [transform_path(path) for path in exts_path.iterdir()]

        def _ext_filter(path: str):
            try:
                module = importlib.import_module(path)
                return hasattr(module, 'setup')
            except Exception:
                # uhh, failed to import. extension is bugged?
                # let it through if it was in the previous load list (maybe some random syntax error during a hot
                # reload, we want to be able to load this again later), otherwise just discard.
                previously_included = path in self._extension_load_list
                if not previously_included:
                    self.log.exception('Excluding %s from the load list:', path)
                else:
                    self.log.warning('%s has failed to load, but it will be retained in the load list because it was '
                                     'previously included.', path)
                return previously_included

        paths = list(filter(_ext_filter, paths))

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
        if self.cfg.hot_reload:
            self.log.debug('Setting up hot reload.')
            self._hot_task = self.loop.create_task(self._hot_reload())

    async def on_message(self, message: discord.Message):
        # Ignore bots if applicable.
        if self.cfg.ignore_bots and message.author.bot:
            return

        # Grab a context, then invoke it.
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def on_command_error(self, ctx: Context, exception: Exception):
        # handled by errors.py
        pass

    def _loop_setup(self):
        self.log.debug('Setting up loop.')
        self.loop.set_exception_handler(exception_handler)


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
