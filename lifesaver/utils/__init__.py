# encoding: utf-8

from collections import Mapping as _Mapping

from .formatting import *
from .system import *
from .messages import *
from .paginator import *


def merge_dicts(template, to_merge):
    """Deeply merges a dict onto another dict."""
    for key, value in to_merge.items():
        if isinstance(value, _Mapping):
            new_dict = template[key]
            merge_dicts(new_dict, value)
            template[key] = new_dict
        else:
            template[key] = value
    return template


def dot_access(dict, access: str):
    """Access a dict by dotted string access."""
    item = dict
    for part in access.split('.'):
        item = item[part]
    return item
