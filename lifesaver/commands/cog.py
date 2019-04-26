# encoding: utf-8

__all__ = ['Cog']

import asyncio
import inspect
import logging
import os
from typing import Type

import aiohttp
from discord.ext import commands
from lifesaver.config import Config


class Cog(commands.Cog):
    """The base class for cogs."""

    def __init__(self, bot):
        super().__init__()

        #: The bot instance.
        self.bot = bot

        #: The logger for this cog.
        self.name = type(self).__name__.lower()
        self.log = logging.getLogger('cog.' + self.name)  # type: logging.Logger

        #: A ClientSession for this cog.
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.config = None

        if hasattr(self, '__lifesaver_config_cls__'):
            path = os.path.join(self.bot.config.cog_config_path, self.name + '.yml')
            self.config = self.__lifesaver_config_cls__.load(path)

        self._scheduled_tasks = []
        self._setup_schedules()

    @property
    def loop(self):
        """A shortcut to :attr:`BotBase.loop`."""
        return self.bot.loop

    @property
    def pool(self):
        """A shortcut to :attr:`BotBase.pool`."""
        return self.bot.pool

    @staticmethod
    def with_config(config_cls: Type[Config]):
        def decorator(cls):
            setattr(cls, '__lifesaver_config_cls__', config_cls)
            return cls
        return decorator

    def _schedule_method(self, name: str, method):
        schedule = method.__lifesaver_schedule__

        async def scheduled_function_wrapper():
            if 'wait_until_ready' in schedule:
                await self.bot.wait_until_ready()

            while True:
                if 'initial_sleep' in schedule:
                    await asyncio.sleep(schedule['interval'])

                try:
                    await method()
                except Exception:
                    self.log.exception(f'Exception thrown from scheduled method {name}')

                await asyncio.sleep(schedule['interval'])

        task = self.bot.loop.create_task(scheduled_function_wrapper())
        self._scheduled_tasks.append(task)

    def _setup_schedules(self):
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        for (name, method) in methods:
            if not hasattr(method, '__lifesaver_schedule__'):
                continue

            self._schedule_method(name, method)

    def cog_unload(self):
        for scheduled_task in self._scheduled_tasks:
            self.log.debug('Cancelling scheduled task: %s', scheduled_task)
            scheduled_task.cancel()

        self.loop.create_task(self.session.close())

    @classmethod
    def every(cls, interval: int, **kwargs):
        """A decorator that designates this function to be executed every ``n`` second(s).

        Parameters
        ----------
        interval
            The time interval in seconds.
        wait_until_ready
            Waits until the bot is ready before running.
        initial_sleep
            The number of seconds to sleep before running.
        """

        def outer(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError('You must use Cog.every on a coroutine.')

            func.__lifesaver_schedule__ = {'interval': interval, **kwargs}

            return func

        return outer
