Configuration
=============

.. autoclass:: lifesaver.bot.BotConfig
    :members:

    A bot config file. The only required value is the :attr:`token` field, which
    is required to connect to Discord's gateway and use the REST API.

.. autoclass:: lifesaver.bot.config.BotLoggingConfig
    :members:

    The subconfig for tweaking logging options.
