from discord.ext import commands


class LifesaverCommand(commands.Command):
    def __init__(self, *args, **kwargs):
        """
        :param typing: Specifies whether to send a typing indicator when invoking this command.
        """
        super().__init__(*args, **kwargs)
        self.typing = kwargs.get('typing', False)

    async def invoke(self, ctx):
        if self.typing:
            async with ctx.typing():
                await super().invoke(ctx)
        else:
            await super().invoke(ctx)


def command(*args, **kwargs):
    return commands.command(*args, **kwargs, cls=LifesaverCommand)


