# encoding: utf-8

__all__ = ["merge_defaults", "dot_access"]

from collections.abc import Mapping
from typing import Any, Mapping, MutableMapping


def merge_defaults(
    source: MutableMapping[Any, Any], *, defaults: Mapping[Any, Any]
) -> Mapping[Any, Any]:
    """Deeply merge default values from a mapping onto another."""
    for key, value in defaults.items():
        if isinstance(value, Mapping) and key in source:
            new_mapping = source[key]
            merge_defaults(new_mapping, defaults=value)
            source[key] = new_mapping
        else:
            source[key] = value
    return source


def dot_access(source: Mapping[Any, Any], access: str) -> Any:
    """Deeply access a nested mapping through a string of keys separated by dots.

    Iterables are not supported.
    """
    for part in access.split("."):
        source = source[part]
    return source
