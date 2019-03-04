# encoding: utf-8

__all__ = ['BotConfig']

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


class BotConfig(Config):
    #: The token of the bot.
    token: str

    #: The path to load extensions from.
    extensions_path: str = './exts'

    #: The path for cog-specific configuration files.
    cog_config_path: str = './config'

    #: Ignores bots when processing commands.
    ignore_bots: bool = True

    #: The command prefix to use.
    command_prefix: Union[List[str], str] = '!'

    #: The bot's description.
    description: str = 'A Discord bot.'

    #: PMs help messages.
    pm_help: Union[bool, None] = None

    #: Determines whether mentions work as a prefix.
    command_prefix_include_mentions: bool = True

    #: Enables the hot reloader.
    hot_reload: bool = False

    #: The global bot emoji table.
    emojis: Dict[str, Any] = DEFAULT_EMOJIS

    #: PostgreSQL access credentials.
    postgres: Optional[Dict[str, Any]] = None
