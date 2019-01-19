FAQ
===

.. currentmodule:: lifesaver.bot

.. _global_emoji_table:

What is the global emoji table?
-------------------------------

The global emoji table is a nested mapping of names to emojis, allowing you to
reference them by a string in your commands. For example, ``generic.ok`` points
to "👌" by default. The :meth:`Context.ok` method uses this emoji to react to
messages. Custom emoji IDs can also be used instead of Unicode codepoints, which
makes using custom emoji throughout your code more readable and configurable.

The global emoji table can be modified in your :class:`BotConfig`. Emojis can
be referenced using :meth:`Context.emoji` or :meth:`BotBase.emoji`.

Nested emoji can be referenced using "dot access syntax" (e.g. ``bot.emoji('generic.ok')``
accesses ``bot.config['emojis']['generic']['ok']``).

How do I disable built-in cogs?
-------------------------------

When using the included CLI module, you can prevent built-in cogs from loading
by passing the ``--no-default-cogs`` flag. It's worth mentioning that this will
also prevent Jishaku from loading.

When instantiating your own Lifesaver bot, make sure to pass ``exclude_default=True``
to your :meth:`BotBase.load_all` call.
