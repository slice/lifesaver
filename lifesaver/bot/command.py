from discord.ext import commands


class LifesaverCommand(commands.Command):
    """
    A :class:`commands.Command` subclass that implements additional useful features.
    """

    def __init__(self, *args, typing: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        #: Specifies whether to send typing indicators while the command is running.
        self.typing = typing

    async def invoke(self, ctx):
        if self.typing:
            async with ctx.typing():
                await super().invoke(ctx)
        else:
            await super().invoke(ctx)


def command(*args, **kwargs):
    """
    :func:`commands.command`, but uses :class:`LifesaverCommand` instead.
    """
    return commands.command(*args, **kwargs, cls=LifesaverCommand)


