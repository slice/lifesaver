# encoding: utf-8

__all__ = ["SubcommandInvocationRequired", "Command", "Group", "command", "group"]

from discord.ext import commands
from discord.ext.commands._types import BotT, CogT, Coro, ContextT
from discord.utils import MISSING

from typing import ParamSpec, TypeVar, Any, Callable, Concatenate, Union

P = ParamSpec('P')
T = TypeVar('T')


class SubcommandInvocationRequired(commands.CommandError):
    """A :class:`discord.ext.commands.CommandError` subclass that is raised when a subcommand needs to be invoked."""


class Command(commands.Command[CogT, P, T]):
    """A :class:`discord.ext.commands.Command` subclass that implements additional features."""

    def __init__(self, *args, typing: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #: Specifies whether to send typing indicators while the command is running.
        self.typing = typing

    async def invoke(self, ctx: commands.Context[BotT]) -> None:
        if self.typing:
            async with ctx.typing():
                await super().invoke(ctx)
        else:
            await super().invoke(ctx)


class Group(commands.Group[CogT, P, T]):
    """A :class:`discord.ext.commands.Group` subclass that implements additional features."""

    def __init__(self, *args, hollow: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        #: Specifies whether a subcommand must be invoked.
        self.hollow = hollow

    async def invoke(self, ctx: commands.Context[BotT]) -> None:
        if ctx.view.eof and self.hollow:
            # If we're at the end of the view (meaning there's no more words,
            # so it's impossible to have a subcommand specified), and we need
            # a subcommand, raise.
            raise SubcommandInvocationRequired()
        await super().invoke(ctx)

    def command(self, *args: Any, **kwargs: Any):
        return super().command(*args, cls=Command, **kwargs)

    def group(self, *args: Any, **kwargs: Any):
        return super().group(*args, cls=Group, **kwargs)


def command(name: str = MISSING, **kwargs: Any) -> Callable[
    [
        Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],  # type: ignore # CogT is used here to allow covariance
        ]
    ],
    Command[CogT, P, Any]
]:
    """The command decorator.

    Works exactly like :func:`discord.ext.commands.command`.

    You can pass the ``typing`` keyword argument to wrap the entire command
    invocation in a :meth:`discord.ext.commands.Context.typing`, making the
    bot type for the duration the command runs.
    """
    return commands.command(name, Command, **kwargs)  # type: ignore


def group(name: str = MISSING, **kwargs: Any) -> Callable[
    [
        Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],  # type: ignore # CogT is used here to allow covariance
        ]
    ],
    Group[CogT, P, Any]
]:
    """The command group decorator.

    Works exactly like :func:`discord.ext.commands.group`.

    You can pass the ``hollow`` keyword argument in order to force the command invoker to
    specify a subcommand (raises :class:`lifesaver.commands.SubcommandInvocationRequired`).
    """
    return commands.group(name, Group, **kwargs)  # type: ignore
