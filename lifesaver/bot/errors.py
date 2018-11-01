# encoding: utf-8

from lifesaver.errors import LifesaverError


class MessageError(LifesaverError):
    """An exception that is handled by the default Errors cog by responding
    directly with the error's message.
    """
