# encoding: utf-8

__all__ = ["setup_logging"]

import contextlib
import logging
import typing

import lifesaver

# The idea of having setup_logging as a context manager is from Danny's R. Danny:
# https://github.com/Rapptz/RoboDanny/blob/1013d990b2e8fb343389e5ec7ffeeda4a8c449da/launcher.py#L25


@contextlib.contextmanager
def setup_logging(config: lifesaver.bot.config.BotLoggingConfig):
    """A context manager that sets up logging according to a :class:`lifesaver.bot.config.BotLoggingConfig`.
    Gracefully destroys handlers when exited.
    """
    try:
        root_logger = logging.getLogger()
        root_logger.setLevel(config.level)

        formatter = logging.Formatter(config.format, config.time_format, style="{")

        file_stream = logging.FileHandler(config.file, encoding="utf-8")
        stream = logging.StreamHandler()

        stream.setFormatter(formatter)
        file_stream.setFormatter(formatter)

        root_logger.addHandler(stream)
        root_logger.addHandler(file_stream)

        yield
    finally:
        handlers = root_logger.handlers[:]
        for handler in handlers:
            handler.close()
            root_logger.removeHandler(handler)
