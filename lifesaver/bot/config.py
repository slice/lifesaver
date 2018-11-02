# encoding: utf-8
from typing import Union, List, Dict, Any

from lifesaver.config import Config


class BotConfig(Config):
    #: The token of the bot.
    token: str

    #: The path from which to load extension files from.
    extensions_path: str = './exts'

    #: The path for cog-specific configuration files
    cog_config_path: str = './config'

    #: Ignores bots when processing commands.
    ignore_bots: bool = True

    #: The command prefix to use.
    command_prefix: Union[List[str], str] = '!'

    #: The bot's description.
    description: str = 'A Discord bot.'

    #: PMs help messages.
    pm_help: Union[bool, None] = None

    #: Includes mentions as valid prefixes.
    command_prefix_include_mentions: bool = True

    #: Activates the hot reloader.
    hot_reload: bool = False

    #: Bot emojis.
    emojis: Dict[str, Union[str, int]]

    #: Postgres access credentials.
    postgres: Dict[str, Any] = None
