# encoding: utf-8

__all__ = ['merge_dicts', 'dot_access']

from collections import Mapping
from typing import Any


def merge_dicts(template: dict, to_merge: dict) -> dict:
    """Deeply merge a dict onto another dict."""
    for key, value in to_merge.items():
        if isinstance(value, Mapping) and key in template:
            new_dict = template[key]
            merge_dicts(new_dict, value)
            template[key] = new_dict
        else:
            template[key] = value
    return template


def dot_access(source: dict, access: str) -> Any:
    """Access a dict by dotted string access."""
    item = source
    for part in access.split('.'):
        item = item[part]
    return item
