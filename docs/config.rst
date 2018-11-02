Configuration
=============

.. autoclass:: lifesaver.bot.BotConfig
    :members:

    .. attribute:: bot_class

        The custom bot class to instantiate when using the CLI module.

        It is formatted as an import path and class separated by a colon, like::

            coolbot5000.bot:CustomBotClass

    .. autoattribute:: command_prefix

        Can be a string or a list of strings.

    .. autoattribute:: description

        Shown in the bot's help command.
