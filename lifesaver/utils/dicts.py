# encoding: utf-8

__all__ = ["merge_defaults", "dot_access"]

from collections.abc import Mapping
from typing import Any, Mapping, MutableMapping


def merge_defaults(
    source: MutableMapping[Any, Any], *, defaults: Mapping[Any, Any]
) -> None:
    """Deeply merge default values from a mapping onto another."""
    for default_key, default_value in defaults.items():
        if (
            isinstance(default_value, Mapping)
            and default_key in source
            and isinstance(source[default_key], Mapping)
        ):
            merge_defaults(source[default_key], defaults=default_value)
        elif default_key not in source:
            source[default_key] = default_value


def dot_access(source: Mapping[Any, Any], access: str) -> Any:
    """Deeply access a nested mapping through a string of keys separated by dots.

    Iterables are not supported.
    """
    for part in access.split("."):
        source = source[part]
    return source
