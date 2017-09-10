from typing import Any

from ruamel.yaml import YAML

NO_DEFAULT = object()


class Field:
    def __init__(self, field_type, *, default=NO_DEFAULT, optional: bool=False):
        self.type = field_type
        self.default = default
        self.optional = optional


class ConfigError(Exception):
    """An error thrown by the Config loader."""
    pass


class Config:
    def __init__(self, data, *, loaded_from=None):
        self.loaded_from = loaded_from

        # For every field specified...
        for key in dir(self):
            # Get the field object provided.
            field = getattr(self, key)

            # Not a field, skip.
            if not isinstance(field, Field):
                continue

            if key not in data and (not field.optional and field.default is NO_DEFAULT):
                raise ConfigError('Missing required config field: {}'.format(key))

            # If we get here and field.default is NO_DEFAULT, then optional=True was provided but no default value
            # was provided, so just fall back to None.
            value = data.get(key, None if field.default is NO_DEFAULT else field.default)

            if field.type is not Any and not isinstance(value, field.type):
                raise ConfigError('Expected field value of type "{}" for {}, instead got value of type "{}".'
                                  .format(type(field.type).__name__, key, type(value).__name__))

            self.__dict__[key] = value

    @classmethod
    def load(cls, file):
        """
        Creates a new :class:`Config` and loads a YAML file into it.

        :param file: The filename to load from.
        :type file: str
        :return: The newly created configuration.
        """
        with open(file, 'r') as fp:
            yaml = fp.read()
            return cls(YAML(typ='safe').load(yaml), loaded_from=file)

    def to_dict(self):
        """
        :return: This :class:`Config` as a dict.
        :rtype: dict
        """
        return self.__dict__
