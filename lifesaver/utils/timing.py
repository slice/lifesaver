# encoding: utf-8

"""Various utilities for timing and ratelimiting."""

"""
MIT License

Copyright (c) 2018 slice

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

__all__ = ["Timer", "format_seconds", "Ratelimiter"]

import time
import typing as T

from discord.ext import commands


def format_seconds(seconds: int) -> str:
    """Format a number of seconds into a readable string."""

    s = seconds
    ms = seconds * 1000
    mcs = seconds * 1_000_000

    if ms > 1000:
        return f"{s:.2f}s"
    elif ms < 1:
        return f"{mcs:.2f}μs"
    else:
        return f"{ms:.2f}ms"


class Timer:
    """A context manager timing utility used to measure time."""

    def __init__(self):
        self.begin: int = None
        self.end: int = None

    def __enter__(self):
        self.begin = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.monotonic()

    @property
    def duration(self):
        """Return the duration that this timer ran, in seconds."""
        return self.end - self.begin

    @property
    def milliseconds(self):
        """Return the duration that this timer ran, in milliseconds."""
        return self.duration * 1000

    ms = milliseconds

    @property
    def microseconds(self):
        """Return the duration that this timer ran, in microseconds."""
        return self.duration * 1_000_000

    def __str__(self):
        return format_seconds(self.duration)


class Ratelimiter:
    """
    A timing mechanism to limit requests to ``rate`` per ``per`` seconds.
    """

    def __init__(self, rate: int, per: float) -> None:
        self.rate = rate
        self.per = per

        self._buckets: T.Dict[T.Any, T.Tuple[float, int]] = {}

    def remaining_time(self, token: T.Any) -> float:
        """Return the time remaining until a token is able to make more requests.

        If the token isn't being rate limited, then ``0.0`` is returned.
        """
        if not self.is_being_rate_limited(token):
            return 0.0

        last_updated, _ = self._buckets[token]
        time_since_last_update = time.monotonic() - last_updated
        return self.per - time_since_last_update

    def is_being_rate_limited(self, token: T.Any) -> bool:
        """Return whether a token is being ratelimited or not.

        This doesn't count against the number of requests allowed within the
        time period.
        """
        return self.hit(passive=True)

    def hit(self, token: T.Any = True, *, passive: bool = False) -> bool:
        """Add one to the number of performed requests, and return whether the
        limit within the timing period has been exceeded."""

        if token not in self._buckets:
            # initial creation
            #
            # the initial value is 1 instead of 0 because the creation counts as
            # a request still
            if not passive:
                self._buckets[token] = (time.monotonic(), 1)
            return False

        last_updated, n_requests = self._buckets[token]
        time_since_last_update = time.monotonic() - last_updated

        if time_since_last_update > self.per:
            # enough time has passed, reset tracking values
            self._buckets[token] = (time.monotonic(), 1)
            return False

        if n_requests + 1 > self.rate:
            # this request would exceed the amount of requests allowed within
            # time period (being ratelimited)
            return True

        if not passive:
            # update the last updated timestamp and number of requests
            self._buckets[token] = (time.monotonic(), self._buckets[token][1] + 1)

        return False

    def __repr__(self) -> str:
        return f"<Ratelimiter rate={self.rate} per={self.per}>"

    def __eq__(self, other) -> bool:
        return self.rate == other.rate and self.per == other.per
