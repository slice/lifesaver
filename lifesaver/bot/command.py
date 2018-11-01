# encoding: utf-8

from discord.ext import commands


class SubcommandInvocationRequired(commands.CommandError):
    """A :class:`CommandError` subclass raised when a subcommand needs to be invoked."""
    pass


class Command(commands.Command):
    """A :class:`commands.Command` subclass that implements additional useful features."""

    def __init__(self, *args, typing: bool = False, **kwargs) -> None:
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
    def __init__(self, *args, hollow: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #: Specifies whether a subcommand must be invoked.
        self.hollow = hollow

    async def invoke(self, ctx):
        if ctx.view.eof and self.hollow:
            # If we're at the end of the view (meaning there's no more words,
            # so it's impossible to have a subcommand specified), and we need
            # a subcommand, raise.
            raise SubcommandInvocationRequired()
        await super().invoke(ctx)


def group(*args, **kwargs):
    return command(*args, cls=Group, **kwargs)


def custom_group(*args, cls, **kwargs):
    return command(*args, cls=cls, **kwargs)


def command(name: str = None, cls=Command, **kwargs):
    return commands.command(name, cls, **kwargs)
