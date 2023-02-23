# encoding: utf-8

__all__ = [
    "MENTION_RE",
    "format_list",
    "escape_backticks",
    "human_delta",
    "codeblock",
    "truncate",
    "Table",
    "clean_mentions",
    "pluralize",
    "format_traceback",
]

"""Text formatting and processing utilities."""

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
import functools
import os
import pathlib
import re
import traceback
from typing import Any, Callable, TypeVar, Union, Optional

import discord

MENTION_RE = re.compile(r"<@!?&?(\d{15,21})>|(@everyone|@here)")
_T = TypeVar("_T")


def _default_list_formatter(value: Any, index: int) -> str:
    return f"{index + 1}. {value}"


def format_list(
    items: list[_T], formatter: Optional[Callable[[_T, int], str]] = None
) -> str:
    """Format a list as an ordered list, with numerals preceding every item.
    List numerals are padded to ensure that there are at least 3 digits.
    """
    formatter = formatter or _default_list_formatter
    return "\n".join(formatter(value, index) for index, value in enumerate(items))


def escape_backticks(text: str) -> str:
    """Replace backticks with a homoglyph to prevent text in codeblocks and
    inline code segments from escaping.
    """
    return text.replace("\N{GRAVE ACCENT}", "\N{MODIFIER LETTER GRAVE ACCENT}")


SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = DAY * 365


def human_delta(
    delta: Union[int, float, datetime.datetime, datetime.timedelta],
    *,
    short: bool = True,
) -> str:
    """Convert a time unit to a human readable time delta string.

    Parameters
    ----------
    delta
        The amount of time to convert.
    short
        Controls whether only the three biggest units of time end up in the result or all.
        Defaults to True.

    Returns
    -------
    str
        A human readable version of the time.
    """
    if isinstance(delta, datetime.datetime):
        delta = discord.utils.utcnow() - delta

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

    units = [
        ("y", years),
        ("mo", months),
        ("d", days),
        ("h", hours),
        ("m", minutes),
        ("s", seconds),
    ]
    periods = [f"{value}{name}" for name, value in units if value > 0]

    if len(periods) > 2:
        if short:
            # Only the biggest three.
            return f"{periods[0]}, {periods[1]} and {periods[2]}"

        return f'{", ".join(periods[:-1])} and {periods[-1]}'
    return " and ".join(periods)


def codeblock(code: str, *, lang: str = "", escape: bool = True) -> str:
    """Construct a Markdown codeblock.

    Parameters
    ----------
    code
        The code to insert into the codeblock.
    lang
        The string to mark as the language when formatting.
    escape
        Prevents the code from escaping from the codeblock.

    Returns
    -------
    str
        The formatted codeblock.
    """
    return "```{}\n{}\n```".format(
        lang,
        escape_backticks(code) if escape else code,
    )


def truncate(text: str, desired_length: int, *, suffix: str = "...") -> str:
    """
    Truncates text and returns it. Three periods will be inserted as a suffix.

    Parameters
    ----------
    text
        The text to truncate.
    desired_length
        The desired length.
    suffix
        The text to insert before the desired length is reached.
        By default, this is "..." to indicate truncation.

    Returns
    -------
    str
        The truncated text.
    """
    if len(text) > desired_length:
        return text[: desired_length - len(suffix)] + suffix
    else:
        return text


class Table:
    """A class to format tabular data into rows and columns.

    Example
    -------
    >>> table = Table('Row 1', 'Row 2')
    >>> table.add_row('Data 1', 'Data 2')
    >>> await table.render()
    Row 1  | Row 2
    -------+--------
    Data 1 | Data 2
    """

    def __init__(self, *column_titles: str) -> None:
        self._rows = [column_titles]
        self._widths: list[int] = []

        for index, entry in enumerate(column_titles):
            self._widths.append(len(entry))

    def _update_widths(self, row: tuple):
        for index, entry in enumerate(row):
            width = len(entry)
            if width > self._widths[index]:
                self._widths[index] = width

    def add_row(self, *row: str):
        """Add a row to the table.

        If the number of data columns specified does not match the number of
        column titles, there may be issues rendering.
        """
        self._rows.append(row)
        self._update_widths(row)

    def add_rows(self, *rows: list[str]):
        for row in rows:
            self.add_row(*row)

    def _render(self):
        def draw_row(row_):
            columns = []

            for index, field in enumerate(row_):
                # Digits get aligned to the right.
                if field.isdigit():
                    columns.append(f" {field:>{self._widths[index]}} ")
                    continue

                # Regular text gets aligned to the left.
                columns.append(f" {field:<{self._widths[index]}} ")

            return "|".join(columns)

        # Column title is centered in the middle of each field.
        title_row = "|".join(
            f" {field:^{self._widths[index]}} "
            for index, field in enumerate(self._rows[0])
        )
        separator_row = "+".join("-" * (width + 2) for width in self._widths)

        drawn = [title_row, separator_row]
        # Remove the title row from the rows.
        self._rows = self._rows[1:]

        for row in self._rows:
            row = draw_row(row)
            drawn.append(row)

        return "\n".join(drawn)

    async def render(self, loop: asyncio.AbstractEventLoop = None):
        """Return a rendered version of the table."""
        loop = loop or asyncio.get_event_loop()

        func = functools.partial(self._render)
        return await loop.run_in_executor(None, func)


def clean_mentions(channel: discord.TextChannel, text: str) -> str:
    """Escape all user and role mentions which would mention someone in the specified channel."""

    def replace(match):
        mention = match.group()

        if "<@&" in mention:
            role_id = int(match.groups()[0])
            role = discord.utils.get(guild.roles, id=role_id)
            if role is not None and role.mentionable:
                mention = f"@{role.name}"

        elif "<@" in mention:
            user_id = int(match.groups()[0])
            member = guild.get_member(user_id)
            if (
                member is not None
                and not member.bot
                and channel.permissions_for(member).read_messages
            ):
                mention = f"@{member.name}"

        if mention in ("@everyone", "@here"):
            mention = mention.replace("@", "@\N{ZERO WIDTH SPACE}")

        return mention

    guild = channel.guild
    return MENTION_RE.sub(replace, text)


def pluralize(
    *, with_quantity: bool = True, with_indicative: bool = False, **word
) -> str:
    """Pluralize a single kwarg's name depending on the value.

    ``with_indicative`` must be used with ``with_quantity``.

    Example
    -------

    >>> pluralize(object=2)
    "2 objects"
    >>> pluralize(object=1)
    "1 object"
    >>> pluralize(object=1, with_quantity=False)
    "object"
    >>> pluralize(object=2, with_quantity=False)
    "objects"
    >>> pluralize(object=2, with_indicative=True)
    "2 objects are"
    >>> pluralize(object=1, with_indicative=True)
    "1 object is"
    """

    try:
        items = word.items()
        kwargs = {"with_quantity", "with_indicative"}
        key = next(item[0] for item in items if item not in kwargs)
    except KeyError:
        raise ValueError("Cannot find kwarg key to pluralize")

    value = word[key]

    with_s = key + ("" if value == 1 else "s")
    indicative = ""

    if with_indicative:
        indicative = " is" if value == 1 else " are"

    if with_quantity:
        return f"{value:,} {with_s}{indicative}"

    return with_s + indicative


def format_traceback(
    exc: BaseException, *, limit: int = 7, hide_paths: bool = False
) -> str:
    """Format an exception into a traceback, akin to ones emitted by the
    interpreter during runtime.

    Parameters
    ----------
    limit
        The maximum number of lines to include.
    hide_paths
        Conceals the current working directory and packages path.
    """

    formatted = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__, limit=limit)
    )

    if hide_paths:
        # Hide the current working directory to shorten text.
        formatted = formatted.replace(os.getcwd(), "/...")

        # Hide the path to the Python packages directory to shorten text.
        packages_dir = str(pathlib.Path(discord.__file__).parent.parent.resolve())
        formatted = formatted.replace(packages_dir, "/packages")

    return formatted
