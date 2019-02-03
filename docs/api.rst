.. currentmodule:: lifesaver

API Reference
=============

Subclasses
----------

Lifesaver subclasses several Discord.py classes in order to provide extra
functionality.

Bot
~~~

These classes gain their functionality from :class:`lifesaver.bot.BotBase`.

.. autoclass:: lifesaver.bot.Bot

    A plain bot, using :class:`lifesaver.bot.BotBase` and
    :class:`discord.Client`.

.. autoclass:: lifesaver.bot.AutoShardedBot

    An autosharded bot, using :class:`lifesaver.bot.BotBase` and
    :class:`discord.AutoShardedClient`.

.. autoclass:: lifesaver.bot.Selfbot

    A selfbot, using :class:`lifesaver.bot.BotBase` and
    :class:`discord.Client`.

    Automatically passes ``bot=False`` when calling ``run()``.

BotBase
~~~~~~~

.. autoclass:: lifesaver.bot.BotBase
    :members:

    This is a :class:`discord.ext.commands.bot.BotBase` subclass that is
    used by :class:`lifesaver.bot.Bot`, :class:`lifesaver.bot.AutoShardedBot`,
    and :class:`lifesaver.bot.Selfbot`. It provides most of the custom
    functionality that Lifesaver bots use.


Context
~~~~~~~

.. autoclass:: lifesaver.bot.Context
    :members:

    This context is automatically used by :class:`lifesaver.bot.Bot` and similar
    classes. It also provides extra functionality.

Utilities
---------

Dictionaries
~~~~~~~~~~~~

.. automodule:: lifesaver.utils.dicts
    :members:

Formatting
~~~~~~~~~~

.. automodule:: lifesaver.utils.formatting
    :members:

.. autoclass:: lifesaver.utils.formatting.Table
    :members:

Roles
~~~~~

.. automodule:: lifesaver.utils.roles
    :members:

System
~~~~~~

.. automodule:: lifesaver.utils.system
    :members:

Timing
~~~~~~

.. automodule:: lifesaver.utils.timing
    :members:

Config
------

.. autoclass:: lifesaver.config.Config
    :members:

Exceptions
----------

.. autoclass:: lifesaver.errors.LifesaverError
    :members:
