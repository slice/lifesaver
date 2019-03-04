# encoding: utf-8

__all__ = ['merge_dicts', 'dot_access']

import collections
from typing import MutableMapping, Mapping, Any


def merge_dicts(template: MutableMapping[Any, Any], to_merge: Mapping[Any, Any]) -> Mapping[Any, Any]:
    """Deeply merge a mapping onto another mapping."""
    for key, value in to_merge.items():
        if isinstance(value, collections.abc.Mapping) and key in template:
            new_dict = template[key]
            merge_dicts(new_dict, value)
            template[key] = new_dict
        else:
            template[key] = value
    return template


def dot_access(source: Mapping[Any, Any], access: str) -> Any:
    """Access a dict by dotted string access."""
    item = source
    for part in access.split('.'):
        item = item[part]
    return item
