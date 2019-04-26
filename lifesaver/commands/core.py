# encoding: utf-8

__all__ = ['SubcommandInvocationRequired', 'Command', 'Group', 'command', 'group']

from discord.ext import commands


class SubcommandInvocationRequired(commands.CommandError):
    """A :class:`discord.ext.commands.CommandError` that is subclass raised when a subcommand needs to be invoked."""


class Command(commands.Command):
    """A :class:`discord.ext.commands.Command` subclass that implements additional features."""

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


class Group(commands.Group, Command):
    """A :class:`discord.ext.commands.Group` subclass that implements additional features."""

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

    def command(self, *args, **kwargs):
        def decorator(func):
            kwargs.setdefault('parent', self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(self, *args, **kwargs):
        def decorator(func):
            kwargs.setdefault('parent', self)
            result = group(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator


def command(name: str = None, cls=Command, **kwargs):
    """The command decorator.

    Works exactly like :func:`discord.ext.commands.command`.

    You can pass the ``typing`` keyword argument to wrap the entire command
    invocation in a :meth:`discord.ext.commands.Context.typing`, making the
    bot type for the duration the command runs.
    """
    return commands.command(name, cls, **kwargs)


def group(name: str = None, **kwargs):
    """The command group decorator.

    Works exactly like :func:`discord.ext.commands.group`.

    You can pass the ``hollow`` keyword argument in order to force the command invoker to
    specify a subcommand (raises :class:`lifesaver.commands.SubcommandInvocationRequired`).
    """
    return command(name, Group, **kwargs)
