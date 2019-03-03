# encoding: utf-8

"""Various utilities for timing and ratelimiting."""

"""
MIT License

Copyright (c) 2018 slice, Rapptz

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

__all__ = ['Timer', 'format_seconds', 'Ratelimiter']

from time import monotonic

from discord.ext import commands


def format_seconds(seconds: int) -> str:
    s = seconds
    ms = seconds * 1000
    mcs = seconds * 1000000

    if ms > 1000:
        return f'{s:.2f}s'
    elif ms < 1:
        return f'{mcs:.2f}μs'
    else:
        return f'{ms:.2f}ms'


class Timer:
    """A context manager timing utility used to measure time."""

    def __init__(self):
        self.begin: int = None
        self.end: int = None

    def __enter__(self):
        self.begin = monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = monotonic()

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
        return self.duration * 1000000

    def __str__(self):
        return format_seconds(self.duration)


# https://github.com/Rapptz/RoboDanny/blob/87772388eff2feeeabe1585efcffaffec9fe37a9/cogs/buttons.py#L89
class Ratelimiter(commands.CooldownMapping):
    def __init__(self, rate, per):
        super().__init__(commands.Cooldown(rate, per, commands.BucketType.user))

    def __repr__(self):
        return f'<Ratelimiter rate={self.rate} per={self.per}>'

    def __eq__(self, other):
        if not isinstance(other, Ratelimiter):
            return False
        return self.rate == other.rate and self.per == other.per

    @property
    def rate(self):
        return self._cooldown.rate

    @property
    def per(self):
        return self._cooldown.per

    def _bucket_key(self, v):
        return v

    def is_rate_limited(self, *args):
        bucket = self.get_bucket(args)
        return bucket.update_rate_limit() is not None
