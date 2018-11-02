# encoding: utf-8

__all__ = ['setup_logging']

import contextlib
import logging
import typing

# The idea of having setup_logging as a context manager is from Danny's R. Danny:
# https://github.com/Rapptz/RoboDanny/blob/1013d990b2e8fb343389e5ec7ffeeda4a8c449da/launcher.py#L25


@contextlib.contextmanager
def setup_logging(time_formatting: str = None, hush: typing.List[str] = None):
    """Context manager that sets up logging in the block. Gracefully destroys handlers when exited.

    The root logger's level is set to logging.DEBUG.
    The ``websockets`` and ``discord`` root loggers are set to ``logging.INFO``.

    Parameters
    ----------
    time_formatting
        The time formatting specifier.
    hush
        A list of additional logger names to set to ``logging.INFO``.
    """

    try:
        time_formatting = time_formatting or '%Y-%m-%d %H:%M:%S'

        # Set the root logger's info to INFO.
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # formatters
        fmt = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', time_formatting, style='{')

        # enable debug logging for us, but not for discord
        default_hush = ['websockets', 'discord']
        for log in (hush + default_hush if hush else default_hush):
            logging.getLogger(log).setLevel(logging.INFO)

        file_stream = logging.FileHandler('bot.log', encoding='utf-8')
        stream = logging.StreamHandler()

        stream.setFormatter(fmt)
        file_stream.setFormatter(fmt)

        root_logger.addHandler(stream)
        root_logger.addHandler(file_stream)

        yield
    finally:
        handlers = root_logger.handlers[:]
        for handler in handlers:
            handler.close()
            root_logger.removeHandler(handler)
