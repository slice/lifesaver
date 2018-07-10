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

import logging
from typing import List

__all__ = ['setup_logging']


def setup_logging(time_formatting: str = '%Y-%m-%d %H:%M', hush: List[str] = None):
    """
    Sets up logging.

    The root logger's level is set to logging.DEBUG.
    The ``websockets`` and ``discord`` root loggers are set to ``logging.INFO``.

    Parameters
    ----------
    time_formatting : str
        The time formatting specifier.
    hush : list of str
        A list of additional logger names to set to ``logging.INFO``.
    """

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
