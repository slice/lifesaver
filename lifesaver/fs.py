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
import asyncio
import logging
import os
import re
from collections import defaultdict

HASHED_FILENAME = re.compile(r'[a-f0-9]{8,}')


class Poller:
    def __init__(self, path: str, *, polling_interval: float = 0.5, name: str = None):
        self.name = name or path
        self.log = logging.getLogger(__name__)
        self.path = path
        self.polling_interval = polling_interval
        self.state = self.build_state()
        self.log.debug('%s: built initial state: %s', self.name, self.state)

    def __repr__(self):
        return f'<Poller path={self.path} polling_interval={self.polling_interval}>'

    def _filter(self, filename) -> str:
        match = HASHED_FILENAME.search(filename)
        if match is not None:
            self.log.debug('%s: skipping %s, hashed', self.name, filename)
        return match is None

    def build_state(self):
        return {
            filename: os.path.getmtime(os.path.join(self.path, filename))
            for filename in os.listdir(self.path)
            if self._filter(filename)
        }

    def detect(self):
        new_state = self.build_state()
        new_state_filenames = set(new_state.keys())
        old_state_filenames = set(self.state.keys())
        changes = defaultdict(set)

        if new_state == self.state:
            return None

        changes['deleted'] = old_state_filenames - new_state_filenames
        changes['created'] = new_state_filenames - old_state_filenames
        changes['updated'] = set(
            filename for (filename, modified) in new_state.items()
            if filename in self.state and modified != self.state[filename]
        )

        self.state = new_state
        return changes

    async def __aiter__(self):
        while True:
            changes = self.detect()
            if changes is not None:
                self.log.debug('%s: yielding changes: %s', self.name, changes)
                yield changes
            await asyncio.sleep(self.polling_interval)
