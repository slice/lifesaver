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
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, Set, DefaultDict

from lifesaver.utils import transform_path

HotEvent = Dict[str, Set[str]]

HASHED_FILENAME = re.compile(r'[a-f0-9]{8,}')

log = logging.getLogger(__name__)


def remove_from_modules(module: str):
    try:
        del sys.modules[module]
    except KeyError:
        pass


class PollerPlug:
    """A receiver for Poller events. Loads and unloads extensions as necessary for a bot instance."""

    def __init__(self, bot):
        self.bot = bot

    def try_load(self, name: str):
        try:
            self.bot.load_extension(name)
        except Exception:
            log.exception('failed to hotload %s:', name)

    def resolve_module(self, filename: str) -> str:
        return transform_path(Path(self.bot.config.extensions_path) / filename)

    def handle(self, event: HotEvent):
        # load new extensions
        for created in event['created']:
            module = self.resolve_module(created)
            log.debug('loading new extension: %s', module)
            self.try_load(created)

        # unload deleted extensions
        for deleted in event['deleted']:
            module = self.resolve_module(deleted)

            if module in self.bot.extensions:
                log.debug('unloading deleted extension: %s', module)
                self.bot.unload_extension(module)

            remove_from_modules(module)

        # reload updated extensions
        for updated in event['updated']:
            module = self.resolve_module(updated)
            log.debug('reloading changed file %s', module)

            if module in self.bot.extensions:
                self.bot.unload_extension(module)

            remove_from_modules(module)
            self.try_load(module)


class Poller:
    """A time-based poller for shallow filesystem changes."""

    def __init__(
        self,
        path: str,
        *,
        polling_interval: float = 0.5,
        name: str = None
    ) -> None:
        self.name = name or path
        self.path = path
        self.polling_interval = polling_interval
        self.state = self.build_state()
        log.debug('%s: built initial state: %s', self.name, self.state)

    def __repr__(self) -> str:
        return f'<Poller path={self.path} polling_interval={self.polling_interval}>'

    def _filter(self, filename: str) -> bool:
        if '__pycache__' in filename or filename.endswith('.pyc'):
            return False

        match = HASHED_FILENAME.search(filename)
        if match is not None:
            log.debug('%s: skipping %s, hashed', self.name, filename)

        return match is None

    def build_state(self) -> Dict[str, float]:
        return {
            filename: os.path.getmtime(os.path.join(self.path, filename))
            for filename in os.listdir(self.path)
            if self._filter(filename)
        }

    def detect(self) -> Optional[HotEvent]:
        new_state = self.build_state()
        new_state_filenames = set(new_state.keys())
        old_state_filenames = set(self.state.keys())
        changes: DefaultDict[str, set] = defaultdict(set)

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
                log.debug('%s: yielding changes: %s', self.name, changes)
                yield changes
            await asyncio.sleep(self.polling_interval)
