from discord.ext import commands


class Command(commands.Command):
    """A :class:`commands.Command` subclass that implements additional useful features."""

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


class GroupMixin(commands.GroupMixin):
    def command(self, *args, **kwargs):
        def decorator(func):
            cmd = command(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd
        return decorator

    def group(self, *args, **kwargs):
        def decorator(func):
            cmd = group(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd
        return decorator


class Group(GroupMixin, commands.Group, Command):
    pass


def group(*args, **kwargs):
    return command(*args, cls=Group, **kwargs)


def command(name: str = None, cls=Command, **kwargs):
    return commands.command(name, cls, **kwargs)
