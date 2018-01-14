import asyncio
import inspect
import logging


class Cog:
    """A base class for cogs."""

    def __init__(self, bot):
        #: The bot instance.
        self.bot = bot

        #: The logger for this cog.
        self.log = logging.getLogger('cog.' + type(self).__name__.lower())  # type: logging.Logger

        self._scheduled_tasks = []
        self._setup_schedules()

    def _setup_schedules(self):
        # Bypass Python's name mangling.
        unload_key = '_' + type(self).__name__ + '__unload'

        # Grab the original unload function defined in the subclass.
        self._original_unload = getattr(self, unload_key, None)
        setattr(self, unload_key, self.__unload)  # Override.

        for key in dir(self):
            if not hasattr(getattr(self, key), '_schedule'):
                continue

            func = getattr(self, key)
            schedule = func._schedule

            async def wrapped():
                if 'wait_until_ready' in schedule:
                    await self.bot.wait_until_ready()

                while True:
                    if 'initial_sleep' in schedule:
                        await asyncio.sleep(schedule['interval'])
                    await func()
                    await asyncio.sleep(schedule['interval'])

            task = self.bot.loop.create_task(wrapped())
            self._scheduled_tasks.append(task)

    def __unload(self):
        self.log.info('Unloading!')

        for scheduled_task in self._scheduled_tasks:
            self.log.info('Cancelling scheduled task: %s', scheduled_task)
            scheduled_task.cancel()

        if self._original_unload:
            self._original_unload()

    @classmethod
    def every(cls, interval: int, **kwargs):
        """
        A decorator that designates this function to be executed every ``n`` second(s).

        :param interval: The time interval in seconds.
        :param wait_until_ready: Waits until the bot is ready before scheduling.
        :param initial_sleep: Specifies whether to sleep first.
        """

        def outer(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError('Scheduled method is not a coroutine')

            func._schedule = {'interval': interval}
            func._schedule.update(kwargs)

            return func

        return outer
