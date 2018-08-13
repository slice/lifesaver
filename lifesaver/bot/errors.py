class LifesaverError(Exception):
    @property
    def message(self):
        """Return the message of this exception."""
        return str(self)


class MessageError(LifesaverError):
    """
    An exception that is handled by the default Errors cog by responding
    directly with the error's message.
    """
