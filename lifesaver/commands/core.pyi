"""Most of this was borrowed from @bryanforbes. Thank you!"""

from typing import Callable, Optional, List, overload, Type, TypeVar

from discord.ext import commands
from discord.ext.commands._types import _BaseCommand
from discord.ext.commands.core import _CoroType, _CheckPredicate

from .cog import Cog
from .context import Context

CT = TypeVar('CT', bound=commands.Context)

class Command(commands.Command[Context]):
    typing: bool

    # If you change this, make sure to update it!
    def __init__(
        self,
        func: _CoroType,
        *,
        typing: Optional[bool] = ...,
        # ---
        name: str = ...,
        enabled: bool = ...,
        help: Optional[str] = ...,
        brief: Optional[str] = ...,
        usage: Optional[str] = ...,
        aliases: List[str] = ...,
        description: str = ...,
        hidden: bool = ...,
        rest_is_raw: bool = ...,
        ignore_extra: bool = ...,
        cooldown_after_parsing: bool = ...,
        checks: List[_CheckPredicate[Context]] = ...,
        cooldown: commands.Cooldown = ...,
        parent: _BaseCommand = ...,
        cog: Optional[Cog] = ...
    ): ...

class Group(commands.Group[Context], Command):
    hollow: bool

    # If you change this, make sure to update it!
    def __init__(
        self,
        *,
        hollow: Optional[bool] = ...,
        typing: Optional[bool] = ...,
        # ---
        name: str = ...,
        enabled: bool = ...,
        help: Optional[str] = ...,
        brief: Optional[str] = ...,
        usage: Optional[str] = ...,
        aliases: List[str] = ...,
        description: str = ...,
        hidden: bool = ...,
        rest_is_raw: bool = ...,
        ignore_extra: bool = ...,
        cooldown_after_parsing: bool = ...,
        invoke_without_command: bool = ...,
        case_insensitive: bool = ...
    ) -> None: ...
    def command(
        self,
        name: Optional[str] = ...,
        *,
        typing: Optional[bool] = ...,
        # ---
        enabled: bool = ...,
        help: Optional[str] = ...,
        brief: Optional[str] = ...,
        usage: Optional[str] = ...,
        aliases: List[str] = ...,
        description: str = ...,
        hidden: bool = ...,
        rest_is_raw: bool = ...,
        ignore_extra: bool = ...,
        cooldown_after_parsing: bool = ...
    ) -> Callable[[_CoroType], Command]: ...
    def group(
        self,
        name: str = ...,
        *,
        hollow: Optional[bool] = ...,
        typing: Optional[bool] = ...,
        # ---
        enabled: bool = ...,
        help: Optional[str] = ...,
        brief: Optional[str] = ...,
        usage: Optional[str] = ...,
        aliases: List[str] = ...,
        description: str = ...,
        hidden: bool = ...,
        rest_is_raw: bool = ...,
        ignore_extra: bool = ...,
        cooldown_after_parsing: bool = ...,
        invoke_without_command: bool = ...,
        case_insensitive: bool = ...
    ) -> Callable[[_CoroType], "Group"]: ...

@overload
def command(
    name: Optional[str] = ...,
    *,
    typing: Optional[bool] = ...,
    # ---
    enabled: bool = ...,
    help: Optional[str] = ...,
    brief: Optional[str] = ...,
    usage: Optional[str] = ...,
    aliases: List[str] = ...,
    description: str = ...,
    hidden: bool = ...,
    rest_is_raw: bool = ...,
    ignore_extra: bool = ...,
    cooldown_after_parsing: bool = ...
) -> Callable[[_CoroType], Command]: ...
@overload
def command(
    name: Optional[str] = ...,
    cls: Optional[Type[commands.Command[CT]]] = ...,
    *,
    enabled: bool = ...,
    help: Optional[str] = ...,
    brief: Optional[str] = ...,
    usage: Optional[str] = ...,
    aliases: List[str] = ...,
    description: str = ...,
    hidden: bool = ...,
    rest_is_raw: bool = ...,
    ignore_extra: bool = ...,
    cooldown_after_parsing: bool = ...
) -> Callable[[_CoroType], commands.Command[CT]]: ...
@overload
def group(
    name: str = ...,
    *,
    hollow: Optional[bool] = ...,
    typing: Optional[bool] = ...,
    # ---
    enabled: bool = ...,
    help: Optional[str] = ...,
    brief: Optional[str] = ...,
    usage: Optional[str] = ...,
    aliases: List[str] = ...,
    description: str = ...,
    hidden: bool = ...,
    rest_is_raw: bool = ...,
    ignore_extra: bool = ...,
    cooldown_after_parsing: bool = ...,
    invoke_without_command: bool = ...,
    case_insensitive: bool = ...
) -> Callable[[_CoroType], Group]: ...
@overload
def group(
    name: str = ...,
    *,
    cls: Optional[Type[commands.Group[CT]]] = ...,
    enabled: bool = ...,
    help: Optional[str] = ...,
    brief: Optional[str] = ...,
    usage: Optional[str] = ...,
    aliases: List[str] = ...,
    description: str = ...,
    hidden: bool = ...,
    rest_is_raw: bool = ...,
    ignore_extra: bool = ...,
    cooldown_after_parsing: bool = ...,
    invoke_without_command: bool = ...,
    case_insensitive: bool = ...
) -> Callable[[_CoroType], commands.Group[CT]]: ...
