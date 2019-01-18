.. currentmodule:: lifesaver.bot

Getting Started
===============

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

.. code-block:: sh

    pip3 install -U git+https://github.com/slice/lifesaver

Windows
~~~~~~~

.. code-block:: sh

    py -3 -m pip install -U git+https://github.com/slice/lifesaver

Creating a Config File
----------------------

All configuration files use YAML_ for the sake of simplicity. YAML anchors are
also useful for the :ref:`global emoji table <global_emoji_table>`.

Enter an empty directory and create a file named ``config.yml``. This is where
your bot's configuration file lives.

Let's specify a token::

    token: 'theQuiCK_b-Row-nFOxJ.U.MPsOV-ErtHElAzYdOG'

This alone serves as the bare minimum config file. Other fields may be
specified for further customization -- see :class:`BotConfig`.

Invoking the CLI
----------------

Lifesaver includes a CLI module that automatically prepares a bot and starts it,
performing the following steps:

* uvloop_ is automatically loaded and applied if available.
* Lifesaver looks for your config file at ``config.yml`` and loads it into a
  :class:`BotConfig` instance at runtime.
* The bot class (default or custom) is constructed and started.

With this CLI module, writing a ``run.py``, ``launcher.py``, or any other file
with a similar name should be unnecessary. This feature allows you to quickly
get started creating new bots.

To start the CLI, use the ``-m`` argument of the Python executable to launch
``lifesaver.cli``::

    python3 -m lifesaver.cli

Your bot should now be up and running with the default command prefix: ``!``.
To change the command prefix, modify the :attr:`BotConfig.command_prefix` value
in your config file.

Built-in Cogs
-------------

The CLI module automatically loads Lifesaver's :doc:`included extensions
<cogs>` upon startup.

Jishaku
~~~~~~~

All bots that use Lifesaver also use Jishaku_. Jishaku is a handy development cog
for Discord.py 1.0.0 bots, and it's very useful in helping you debug your bot
as you write it.

Arbitrary Python code can be executed using the ``py`` subcommand of the ``jsk``
command group::

    !jsk py 1 + 1

Jishaku's Python evaluator also has import-expression-parser_ support, allowing
you to quickly import any needed modules within identifiers in your code::

    !jsk py collections!.Counter

Magic locals like ``_ctx``, ``_bot``, ``_msg``, ``_guild``, and ``_channel``
exist in the scope of any code evaluated.

.. _import-expression-parser: https://github.com/bmintz/import-expression-parser
.. _Jishaku: https://github.com/Gorialis/Jishaku
.. _Git: https://git-scm.com/
.. _uvloop: https://uvloop.readthedocs.io/
.. _YAML: https://en.wikipedia.org/wiki/YAML
