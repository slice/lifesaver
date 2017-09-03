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

        # Bypass Python's name mangling.
        setattr(self, '_' + type(self).__name__ + '__unload', self.__unload)

        # Iterate over all keys in myself.
        for key in dir(self):
            # This thing doesn't have a _schedule, so it's probably not scheduled.
            if not hasattr(getattr(self, key), '_schedule'):
                continue

            # Grab the function, and the schedule metadata.
            func = getattr(self, key)
            schedule = func._schedule

            # Wrap the entire function in a loop that runs forever.
            async def wrapped():
                if 'wait_until_ready' in schedule:
                    await self.bot.wait_until_ready()

                while True:
                    if 'initial_sleep' in schedule:
                        await asyncio.sleep(schedule['interval'])
                    await func()
                    await asyncio.sleep(schedule['interval'])

            # Create (and run) the task.
            task = self.bot.loop.create_task(wrapped())

            # Keep track of the tasks.
            self._scheduled_tasks.append(task)

    def __unload(self):
        self.log.info('Unloading!')

        # Cancel all scheduled tasks.
        for scheduled_task in self._scheduled_tasks:
            self.log.info('Cancelling scheduled task: %s', scheduled_task)
            scheduled_task.cancel()

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

            # Add some scheduling metadata.
            func._schedule = {
                'interval': interval
            }

            # Add all kwargs.
            func._schedule.update(kwargs)

            return func
        return outer
