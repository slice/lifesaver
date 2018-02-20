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

import asyncio
import json
import os
import uuid
from typing import Any

from abc import ABC, abstractmethod


class AsyncStorage(ABC):
    @abstractmethod
    async def put(self, key: str, value: Any):
        """
        Puts a value into storage.

        Parameters
        ----------
        key : str
            The key.
        value : str
            The value to insert.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str):
        """
        Returns a value from storage.

        Parameters
        ----------
        key : str
            The key.
        """


class AsyncJSONStorage(AsyncStorage):
    """
    Asynchronous JSON file based storage.

    Based off of RoboDanny's excellent config.py::

        https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/config.py
    """

    def __init__(self, file, *, loop=None):
        """
        Parameters
        ----------
        file : str
            The file to save to.
        loop : asyncio.AbstractEventLoop
            The event loop to use.
        """
        self.file = file
        self._data = {}
        self.loop = loop or asyncio.get_event_loop()
        self.lock = asyncio.Lock()

        # Attempt to load.
        self._load()

    def _save(self):
        # Generate a filename.
        atomic_name = f'{uuid.uuid4()}.tmp'

        # Save to a file with a randomly-generated filename.
        with open(atomic_name, 'w', encoding='utf-8') as fp:
            json.dump(self._data.copy(), fp, ensure_ascii=True, separators=(',', ':'))

        # Rename the "atomic" file to the actual file to prevent corruptions.
        os.replace(atomic_name, self.file)

    def _load(self):
        try:
            with open(self.file, 'r', encoding='utf-8') as fp:
                self._data = json.load(fp)
        except FileNotFoundError:
            self._data = {}

    async def save(self):
        """
        Saves the data in memory to disk.
        """
        async with self.lock:
            await self.loop.run_in_executor(None, self._save)

    async def load(self):
        """
        Loads the data from disk.
        """
        async with self.lock:
            await self.loop.run_in_executor(None, self._load)

    async def put(self, key, value):
        self._data[str(key)] = value
        await self.save()

    async def delete(self, key):
        del self._data[str(key)]
        await self.save()

    def get(self, key, *args):
        return self._data.get(str(key), *args)

    def all(self):
        return self._data

    def __contains__(self, key):
        return str(key) in self._data

    def __getitem__(self, key):
        return self._data[str(key)]

    def __len__(self):
        return len(self._data)
