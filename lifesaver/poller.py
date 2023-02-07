# encoding: utf-8

__all__ = ["HotEvent", "PollerPlug", "Poller"]

import asyncio
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Union, List, Optional, DefaultDict

from lifesaver.load_list import filter_path, transform_path

HotEvent = Dict[str, Set[Path]]

HASHED_FILENAME = re.compile(r"[a-f0-9]{8,}")

log = logging.getLogger(__name__)


class Poller:
    """A crude, timer-based filesystem poller for detecting file creation,
    modification, and deletion.

    It works by repeatedly querying the search paths every ``polling_interval``
    seconds (by default, ``1``).

    **Caveat:** All files are filtered through :func:`lifesaver.load_list.filter_path`,
    and files with hashes (at least 8 consecutive hexadecimal characters) are ignored.

    Example
    -------

    .. code:: python3

        from pathlib import Path
        from typing import Set

        poller = Poller(Path("cool_files/"))

        # This loop will block infinitely, so do this inside of a :class:`asyncio.Task`.
        async for event in poller:
            created_files: Set[Path] = event["created"]
            deleted_files: Set[Path] = event["deleted"]
            updated_files: Set[Path] = event["updated"]
    """

    def __init__(
        self,
        paths: Union[List[Path], Path],
        *,
        polling_interval: float = 1,
        name: Optional[str] = None,
    ) -> None:
        if isinstance(paths, list):
            self.paths = paths
            self.name = name or paths[:1]  # slicing to avoid IndexError
        else:
            self.paths = [paths]
            self.name = name or str(paths)

        self.polling_interval = polling_interval
        self.state = self._build_state()
        self.log = logging.getLogger(f"{__name__}[{self.name}]")

        self.log.debug("watching: %r", self.paths)
        self.log.debug("initial state: %s", self.state)

    def __repr__(self) -> str:
        return (
            f"<Poller paths={self.paths!r} polling_interval={self.polling_interval!r}>"
        )

    def filter_entry(self, entry: Path) -> bool:
        """Return whether a :class:`Path` is appropriate for being included in
        the changeset.
        """
        if not filter_path(entry):
            return False

        match = HASHED_FILENAME.search(str(entry))
        if match is not None:
            self.log.debug("skipping %s, has a hash", str(entry))

        return match is None

    def _build_state(self) -> Dict[Path, float]:
        """Return a dict of all applicable files to their last modified time."""
        state = {}

        for path in self.paths:
            state.update(
                {
                    entry: entry.stat().st_mtime
                    for entry in path.glob("**/*")
                    if entry.is_file() and self.filter_entry(entry)
                }
            )

        return state

    def detect(self) -> Optional[HotEvent]:
        """Diff the old state with a new state, returning a dict describing
        the new changes, or `None` if no changes were detected.
        """
        new_state = self._build_state()
        new_state_filenames = set(new_state.keys())
        old_state_filenames = set(self.state.keys())
        changes: DefaultDict[str, set] = defaultdict(set)

        if new_state == self.state:
            return None

        changes["deleted"] = old_state_filenames - new_state_filenames
        changes["created"] = new_state_filenames - old_state_filenames
        changes["updated"] = set(
            filename
            for (filename, current_mtime) in new_state.items()
            if filename in self.state and current_mtime > self.state[filename]
        )

        self.state = new_state
        return dict(changes)

    async def __aiter__(self):
        while True:
            changes = self.detect()
            if changes is not None:
                self.log.debug("yielding changes: %s", changes)
                yield changes
            await asyncio.sleep(self.polling_interval)


class PollerPlug:
    """A receiver for Poller events which loads, unloads and reloads extensions
    as necessary for a bot instance.

    It receives events emitted by :class:`Poller` and handles the logic for
    you. It also intelligently resolves which extensions to act on based on the
    file modified.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    @property
    def root(self) -> Path:
        """The path to the bot extensions."""
        return Path(self.bot.config.extensions_path)

    async def try_load(self, name: str) -> None:
        """Try to load a bot extension. Logs an exception upon failure."""
        try:
            await self.bot.load_extension(name)
        except Exception:
            log.exception("failed to load %s:", name)

    def _path_is_extension(self, path: Path) -> bool:
        """Return whether a path is is directly under the extensions path.
        (i.e. it is an extension.)

        Keep in mind that a loadable extension can either be a single file
        (``exts/ext.py``) or a module (``exts/ext``, which loads
        ``exts/ext/__init__.py``). This method aims to check for both
        scenarios.
        """
        return path.parent == self.root

    def _resolve_extension_from_subfile(self, path: Path) -> Optional[Path]:
        """Resolve the extension path from an extension subfile.

        Because extensions can be modules, the point of this method is to
        resolve the actual extension path from a file within that extension.

        For example, this would resolve ``exts/ext/db/db.py`` to ``exts/ext``.
        This is useful to find the correct extension path to reload when a
        subfile changes.
        """
        if self._path_is_extension(path):
            raise ValueError(f"Path is not a subfile of an extension module ({path})")
        if self.root not in path.parents:
            raise ValueError("Path is not in the extensions path ({path})")

        # traverse up the file's parents until we get to the extension path.
        for parent in path.parents:
            if self._path_is_extension(parent):
                return parent

        return None

    def resolve_module(
        self, path: Path, *, resolve_subfiles: bool = True
    ) -> Optional[str]:
        """Resolve a path to a changed file to a module to load, unload, or reload."""
        if self._path_is_extension(path):
            # an extension file was changed
            return transform_path(path)

        if not resolve_subfiles:
            # if the caller doesn't want to resolve subfiles, don't.
            #
            # this appropriate when handling deletes, for example. if we delete
            # an extension subfile, we don't want to unload the entire extension.
            return None

        # an extension subfile was changed, we must resolve the extension
        # itself
        #
        # (e.g. if `exts.currency.wallet` changes, we must resolve
        # `exts.currency` from that.)
        extension_path = self._resolve_extension_from_subfile(path)

        if not extension_path:
            raise ValueError(
                f"Cannot resolve extension from extension subfile ({path})"
            )

        extension_module = transform_path(extension_path)
        log.debug("resolved extension %s from path %s", extension_module, path)
        return extension_module

    async def handle(self, event: HotEvent) -> None:
        # load new extensions
        for created in event["created"]:
            module = self.resolve_module(created, resolve_subfiles=False)
            if module is not None:
                log.info("loading new extension %s", module)
                await self.try_load(module)

        # unload deleted extensions
        for deleted in event["deleted"]:
            module = self.resolve_module(deleted, resolve_subfiles=True)

            if module is not None and module in self.bot.extensions:
                log.info("unloading deleted extension %s", module)
                await self.bot.unload_extension(module)

        # reload updated extensions
        for updated in event["updated"]:
            module = self.resolve_module(updated)
            log.info("reloading extension %s", module)

            await self.bot.reload_extension(module)
