import logging


class Cog:
    """A base class for cogs."""

    def __init__(self, bot):
        #: The bot instance.
        self.bot = bot

        #: The logger for this cog.
        self.log = logging.getLogger('cog.' + type(self).__name__.lower())  # type: logging.Logger
