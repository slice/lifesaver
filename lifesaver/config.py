"""
MIT License

Copyright (c) 2017 - 2018 slice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import typing

from ruamel.yaml import YAML

from lifesaver.errors import LifesaverError


class ConfigError(LifesaverError):
    """An error thrown by the Config loader."""


class Config:
    """A bot or cog configuration."""

    def __init__(self, data, *, loaded_from: str = None):
        self.loaded_from = loaded_from
        self.data = data

        for key, value in data.items():
            setattr(self, key, value)

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def __getitem__(self, item):
        return self.data[item]

    @classmethod
    def load(cls, path: str) -> 'Config':
        """Creates a Config instance from a file path.

        Parameters
        ----------
        path
            The path to a YAML file.
        """
        with open(path, 'r') as fp:
            yaml = fp.read()
            return cls(YAML().load(yaml), loaded_from=path)

    @property
    def as_dict(self) -> typing.Dict[typing.Any, typing.Any]:
        """Returns this Config as a dict."""
        return self.data
