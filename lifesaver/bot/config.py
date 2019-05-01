# encoding: utf-8

__all__ = ['BotConfig', 'BotLoggingConfig']

from typing import Union, List, Dict, Optional, Any

from lifesaver.config import Config

YES_EMOJI = '\N{WHITE HEAVY CHECK MARK}'
NO_EMOJI = '\N{CROSS MARK}'
OK_EMOJI = '\N{OK HAND SIGN}'

DEFAULT_EMOJIS = {
    'generic': {
        'yes': YES_EMOJI,
        'no': NO_EMOJI,
        'ok': OK_EMOJI,
    },
}


class BotLoggingConfig(Config):
    #: The logging level to use.
    level: str = 'INFO'

    #: The file to output to.
    file: str = 'bot.log'

    #: The logging format.
    format: str = '[{asctime}] [{levelname}] {name}: {message}'

    #: The time logging format.
    time_format: str = '%Y-%m-%d %H:%M:%S'


class BotConfig(Config):
    #: The token of the bot.
    token: str

    #: The custom bot class to instantiate when using the CLI module.
    #:
    #: It is formatted as an import path and class separated by a colon, like::
    #:
    #:     coolbot.bot:CustomBotClass
    bot_class: Optional[str] = None

    #: The custom config class to use when using the CLI.
    config_class: Optional[str] = None

    #: The logging config to use when using the CLI. See :class:`BotLoggingConfig`.
    logging: BotLoggingConfig

    #: The path to load extensions from.
    extensions_path: str = './exts'

    #: The path for cog-specific configuration files.
    cog_config_path: str = './config'

    #: Ignores bots when processing commands.
    ignore_bots: bool = True

    #: The command prefix to use. Can be a string or a list of strings.
    command_prefix: Union[List[str], str] = '!'

    #: The bot's description. Shown in the help command.
    description: str = 'A Discord bot.'

    #: A tribool describing how the bot should decide to DM help messages.
    #: See :attr:`discord.ext.commands.DefaultHelpCommand.dm_help`.
    dm_help: Optional[bool] = None

    #: Determines whether mentions work as a prefix.
    command_prefix_include_mentions: bool = True

    #: Enables the hot reloader.
    hot_reload: bool = False

    #: The global bot emoji table.
    emojis: Dict[str, Any] = DEFAULT_EMOJIS

    #: PostgreSQL access credentials.
    postgres: Optional[Dict[str, Any]] = None
