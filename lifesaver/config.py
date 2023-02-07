# encoding: utf-8

import inspect
import typing
from collections.abc import Mapping

from ruamel.yaml import YAML
from typing_extensions import Self

from lifesaver.errors import LifesaverError
from lifesaver.utils import merge_defaults


class ConfigError(LifesaverError):
    """An error thrown by the Config loader."""


class Config:
    """A dict-like object that encompasses a configuration of some kind.

    All config files use YAML_ for markup.

    .. _YAML: https://en.wikipedia.org/wiki/YAML
    """

    def __init__(self, data: dict) -> None:
        """Create a new Config instance.

        Parameters
        ----------
        data
            The configuration data.
        """
        self._load_data(data)

    def _load_data(self, data):
        # Grab the type hints as defined in the class.
        # (Can't do it on the instance, or else it doesn't traverse the MRO.)
        hints = typing.get_type_hints(self.__class__)

        for name, hint in hints.items():
            # The default value is already set (it's the class attribute!)
            default_value = getattr(self, name, None)
            value = data.get(name, default_value)

            if inspect.isclass(hint) and issubclass(hint, Config):
                # Load a nested config using the provided inner mapping, or fall
                # back to an empty dict to use the nested config's defaults.
                value = hint(value or {})

            if isinstance(default_value, Mapping) and isinstance(value, dict):
                # Merge the provided dict into the default mapping instead of overwriting.
                value = merge_defaults(value, defaults=default_value)

            setattr(self, name, value)

    @classmethod
    def load(cls, path: str) -> Self:
        """Creates a Config instance from a file path.

        Parameters
        ----------
        path
            A path to a YAML_ file.
        """
        with open(path, "r") as fp:
            yaml = fp.read()
            return cls(YAML().load(yaml))
