# encoding: utf-8

__all__ = ("AsyncStorage", "Storage")

import asyncio
import collections.abc
import json
import os
import tempfile
from abc import abstractmethod
from typing import Iterator, Optional, Any, Type, TypeVar, Callable

T = TypeVar("T")
VT = TypeVar("VT")


class AsyncStorage(collections.abc.Mapping[str, VT]):
    @abstractmethod
    async def put(self, key: str, value: Any) -> None:
        """Insert a value into storage and persist it."""
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str, default: Optional[VT] = None) -> VT:
        """Look up a value in storage."""
        raise NotImplementedError


class Storage(AsyncStorage[VT]):
    """Asynchronous data persistence to a JSON file.

    Based off of RoboDanny's excellent config.py::

        https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/config.py
    """

    def __init__(
        self,
        file: str,
        *,
        encoder: Type[json.JSONEncoder] = json.JSONEncoder,
        object_hook: Optional[Callable[[dict[Any, Any]], Any]] = None,
    ) -> None:
        self.file = file
        self._data: dict[str, Any] = {}
        self.lock = asyncio.Lock()
        self.object_hook = object_hook
        self.encoder = encoder

        self._load()

    def _save(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        ) as temporary_destination:
            json.dump(
                self._data.copy(),
                temporary_destination,
                cls=self.encoder,
                indent=2,
            )

            os.replace(temporary_destination.name, self.file)

    def _load(self) -> None:
        try:
            with open(self.file, "r", encoding="utf-8") as fp:
                self._data = json.load(fp, object_hook=self.object_hook)
        except FileNotFoundError:
            self._data = {}

    async def save(self) -> None:
        """Serialize the in-memory data and atomatically save it to disk."""
        async with self.lock:
            await asyncio.to_thread(self._save)

    async def load(self) -> None:
        """Read the corresponding JSON file from disk and deserialize it (if it exists)."""
        async with self.lock:
            await asyncio.to_thread(self._load)

    async def put(self, key: str, value: VT) -> None:
        self._data[key] = value
        await self.save()

    async def delete(self, key: str) -> None:
        del self._data[key]
        await self.save()

    def get(self, key: str, default: Optional[VT] = None) -> VT:
        return self._data.get(key, default)

    def all(self):
        return self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __contains__(self, key: Any) -> bool:
        return str(key) in self._data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<Storage file={self.file!r}>"
