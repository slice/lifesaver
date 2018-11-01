# encoding: utf-8

__all__ = ['setup_logging']

import logging
from typing import List


def setup_logging(time_formatting: str = None, hush: List[str] = None):
    """Set up logging defaults.

    The root logger's level is set to logging.DEBUG.
    The ``websockets`` and ``discord`` root loggers are set to ``logging.INFO``.

    Parameters
    ----------
    time_formatting
        The time formatting specifier.
    hush
        A list of additional logger names to set to ``logging.INFO``.
    """

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
