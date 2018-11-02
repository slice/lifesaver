# encoding: utf-8

from .formatting import *
from .system import *
from .messages import *
from .paginator import *


def dot_access(dict, access: str):
    """Access a dict by dotted string access."""
    item = dict
    for part in access.split('.'):
        item = item[part]
    return item
