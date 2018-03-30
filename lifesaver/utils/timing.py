# -*- coding: utf-8 -*-
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
from time import monotonic

from lifesaver.utils import human_delta


class Timer:
    """A timing utility used to measure time."""

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
        return self.end - self.begin

    @property
    def ms(self):
        return round(self.duration * 1000, 2)

    def __str__(self):
        return f'{self.ms}ms'
