# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2017 - 2018 slice, FrostLuma

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
from typing import List, Any

import functools


def format_list(lst: List[Any]) -> str:
    """
    Returns a string representing a list as an ordered list. List numerals are padded to ensure that there are at
    least 3 digits.

    Parameters
    ----------
    lst : list of any
        The list to format.

    Returns
    -------
    str
        The formatted string.
    """
    return '\n'.join('`{:03d}`: {}'.format(index + 1, value) for index, value in enumerate(lst))


def escape_backticks(text: str) -> str:
    """
    Replaces backticks with a homoglyph to prevent codeblock and inline code breakout.

    Parameters
    ----------
    text : str
        The text to escape.

    Returns
    -------
    str
        The escaped text.
    """
    return text.replace('\N{GRAVE ACCENT}', '\N{MODIFIER LETTER GRAVE ACCENT}')


SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = DAY * 365


def human_delta(delta, *, short: bool = True) -> str:
    """
    Converts to a human readable time delta.
    Parameters
    ----------
    delta : Union[int, float, datetime.datetime, datetime.timedelta]
        The amount of time to convert
    short : bool
        Controls whether only the three biggest units of time end up in the result or all. Defaults to True.
    Returns
    -------
    str
        A human readable version of the time.
    """
    if isinstance(delta, datetime.datetime):
        delta = datetime.datetime.utcnow() - delta

    if isinstance(delta, datetime.timedelta):
        delta = delta.total_seconds()

    if isinstance(delta, float):
        delta = int(delta)

    if delta <= 0:
        return "0s"

    years, rest = divmod(delta, YEAR)
    months, rest = divmod(rest, MONTH)
    days, rest = divmod(rest, DAY)
    hours, rest = divmod(rest, HOUR)
    minutes, seconds = divmod(rest, MINUTE)

    periods = [("y", years), ("mo", months), ("d", days), ("h", hours), ("m", minutes), ("s", seconds)]
    periods = [f"{value}{name}" for name, value in periods if value > 0]

    if len(periods) > 2:
        if short:
            # only the biggest three
            return f'{periods[0]}, {periods[1]} and {periods[2]}'

        return f'{", ".join(periods[:-1])} and {periods[-1]}'
    return " and ".join(periods)


def codeblock(code: str, *, lang: str = '', escape: bool = True) -> str:
    """
    Constructs a Markdown codeblock.

    Parameters
    ----------
    code : str
        The code to insert into the codeblock.
    lang : str, optional
        The string to mark as the language when formatting.
    escape : bool, optional
        Prevents the code from escaping from the codeblock.

    Returns
    -------
    str
        The formatted codeblock.
    """
    return "```{}\n{}\n```".format(lang, escape_backticks(code) if escape else code)


def truncate(text: str, desired_length: int, *, suffix: str = '...') -> str:
    """
    Truncates text. Three periods will be inserted as a suffix by default, but this can be changed.

    Parameters
    ----------
    text : str
        The text to truncate.
    desired_length : int
        The desired length.
    suffix : str, optional
        The text to insert before the desired length is reached. By default, this is "..." to indicate truncation.
    """
    if len(text) > desired_length:
        return text[:desired_length - len(suffix)] + suffix
    else:
        return text


class Table:
    def __init__(self, *column_titles: str):
        self._rows = [column_titles]
        self._widths = []

        for index, entry in enumerate(column_titles):
            self._widths.append(len(entry))

    def _update_widths(self, row: tuple):
        for index, entry in enumerate(row):
            width = len(entry)
            if width > self._widths[index]:
                self._widths[index] = width

    def add_row(self, *row: str):
        """
        Add a row to the table.
        .. note :: There's no check for the number of items entered, this may cause issues rendering if not correct.
        """
        self._rows.append(row)
        self._update_widths(row)

    def add_rows(self, *rows: List[str]):
        for row in rows:
            self.add_row(*row)

    def _render(self):
        def draw_row(row_):
            columns = []

            for index, field in enumerate(row_):
                # digits get aligned to the right
                if field.isdigit():
                    columns.append(f" {field:>{self._widths[index]}} ")
                    continue

                # regular text gets aligned to the left
                columns.append(f" {field:<{self._widths[index]}} ")

            return "|".join(columns)

        # column title is centered in the middle of each field
        title_row = "|".join(f" {field:^{self._widths[index]}} " for index, field in enumerate(self._rows[0]))
        separator_row = "+".join("-" * (width + 2) for width in self._widths)

        drawn = [title_row, separator_row]
        # remove the title row from the rows
        self._rows = self._rows[1:]

        for row in self._rows:
            row = draw_row(row)
            drawn.append(row)

        return "\n".join(drawn)

    async def render(self, loop: asyncio.AbstractEventLoop = None):
        """Returns a rendered version of the table."""
        loop = loop or asyncio.get_event_loop()

        func = functools.partial(self._render)
        return await loop.run_in_executor(None, func)
