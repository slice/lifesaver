# encoding: utf-8

__all__ = ['BotConfig']

from typing import Union, List, Dict, Any

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
    'exec': {
        'cancelled': OK_EMOJI,
        'kill': '\N{OCTAGONAL SIGN}',
        'waiting': '\N{HOURGLASS WITH FLOWING SAND}',
        'error': '\N{COLLISION SYMBOL}',
        'ok': YES_EMOJI,
    },
}


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
    emojis: Dict[str, Union[str, int]] = DEFAULT_EMOJIS

    #: Postgres access credentials.
    postgres: Dict[str, Any] = None
