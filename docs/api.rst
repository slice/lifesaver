.. currentmodule:: lifesaver

API Reference
=============

Bot
---

Lifesaver subclasses Discord.py's command extension's bot class in order to
provide extra features.

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

Commands
--------

Lifesaver extends the commands extension in order to provide useful features
that you might find helpful. These classes and functions are also available
through the ``lifesaver`` module, because the name of this module would
conflict with imports of ``discord.ext.commands``::

    # ✅ Use lifesaver.Cog, @lifesaver.command, ...
    import lifesaver
    from discord.ext import commands

    # ❌ Clashing namespaces!
    from lifesaver import commands
    frmo discord.ext import commands

Cog
~~~

Lifesaver provides a custom cog class which works exactly like :class:`discord.ext.commands.Cog`,
but provides some useful tools, like an automatically created :class:`aiohttp.ClientSession`,
integration with :class:`lifesaver.config.Config`, and more.

.. autoclass:: lifesaver.commands.Cog
    :members:

Commands
~~~~~~~~

.. autofunction:: lifesaver.commands.command

.. autofunction:: lifesaver.commands.group

.. autoclass:: lifesaver.commands.SubcommandInvocationRequired

.. autoclass:: lifesaver.commands.Command

.. autoclass:: lifesaver.commands.Group

Context
~~~~~~~

.. autoclass:: lifesaver.commands.Context
    :members:

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
