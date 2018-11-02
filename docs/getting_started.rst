Getting Started
===============

.. currentmodule:: lifesaver

Lifesaver is a framework/library for Discord.py 1.0.0. It includes useful logic
and cogs that help reduce boilerplate.

Installing
----------

For now, Lifesaver can only be installed directly from GitHub. Make sure you
have Git_ installed, or else the install will fail.

UNIX
~~~~

Depending on your Python installation, ``pip`` can point to Python 2 or 3.
Assuming it points to Python 2, this example uses ``pip3``.

::

    pip3 install -U git+https://github.com/slice/lifesaver

Windows
~~~~~~~

::

    py -3 -m pip install -U git+https://github.com/slice/lifesaver

Creating a Config File
----------------------

All configuration files use YAML_ for the sake of simplicity. Anchors are also
useful for the global emoji table.

Enter an empty directory and create ``config.yml``. This is where your bot's
configuration file lives.

We'll specify a token for now::

        token: 'theQuiCK_b-Row-nFOxJ.U.MPsOV-ErtHElAzYdOG'

This is the bare minimum config file. Other attributes may be specified for
further customization -- see :class:`lifesaver.bot.BotConfig`.

Invoking the CLI
----------------

Lifesaver includes a CLI module that automatically prepares a bot and starts it,
performing the following steps:

* uvloop_ is automatically used if available.
* Lifesaver looks for your config file at ``config.yml`` and loads it into a
  :class:`lifesaver.bot.BotConfig` instance at runtime.
* The bot class (default or custom) is instantiated and ran.

With this CLI module, writing a ``run.py``, ``launcher.py``, or any other file
with a similar name and task should be unnecessary. It allows you to quickly get
started scaffolding new bots: you don't have to write launcher scripts.

.. _Git: https://git-scm.com/
.. _uvloop: https://uvloop.readthedocs.io/
.. _YAML: https://en.wikipedia.org/wiki/YAML
