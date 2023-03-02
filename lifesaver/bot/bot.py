# encoding: utf-8

"""Main Lifesaver bot classes."""

import logging
from pathlib import Path
from typing import (
    Any,
    Callable,
    Literal,
    overload,
    Iterable,
    Optional,
    TYPE_CHECKING,
    cast,
)

import discord
from discord.ext import commands
from discord.ext.commands import GroupMixin, HelpCommand

import lifesaver
from lifesaver.load_list import LoadList
from lifesaver.poller import Poller, PollerPlug
from lifesaver.utils import dot_access

from .config import BotConfig

if TYPE_CHECKING:
    import asyncpg

INCLUDED_EXTENSIONS = [
    "jishaku",
    "lifesaver.bot.exts.health",
    "lifesaver.bot.exts.errors",
]

PrefixType = Iterable[str] | str | Callable[[Any, discord.Message], Iterable[str]]


def compute_command_prefix(
    cfg: BotConfig,
) -> PrefixType:
    """Compute the appropriate ``command_prefix`` for the bot from the :class:`BotConfig`."""
    prefix = cfg.command_prefix

    if cfg.command_prefix_include_mentions:
        if isinstance(prefix, str):
            return commands.when_mentioned_or(prefix)
        else:
            return commands.when_mentioned_or(*prefix)

    return prefix


class BotBase(commands.bot.BotBase, GroupMixin["lifesaver.Cog"]):
    """The base bot class for Lifesaver bots.

    This is a :class:`discord.ext.commands.bot.BotBase` subclass that is
    used by :class:`lifesaver.bot.Bot` and :class:`lifesaver.bot.AutoShardedBot`.
    It provides most of the custom functionality that Lifesaver bots use.
    """

    def __init__(
        self,
        cfg: BotConfig,
        *,
        command_prefix: Optional[PrefixType] = None,
        description: Optional[str] = None,
        help_command: Optional[HelpCommand] = None,
        # This is `Any` because there doesn't seem to be a way for Python type
        # checkers to infer the rest of the keyword arguments from the
        # superclass, and I don't anticipate users of this library needing this
        # too badly. Otherwise, I'd just copy everything here.
        **kwargs: Any,
    ) -> None:
        """Initialize a BotBase from a :class:`BotConfig` and other kwargs.

        The kwargs override any related BotConfig values and are all passed to
        :class:`commands.bot.BotBase`'s initializer.
        """
        #: The bot's :class:`BotConfig`.
        self.config = cfg

        description = description or cfg.description
        help_command = help_command or commands.DefaultHelpCommand(dm_help=cfg.dm_help)

        intents_specifier = cfg.intents
        intents = discord.Intents.default()
        if isinstance(intents_specifier, list):
            kwargs = {key: True for key in intents_specifier}
            intents = discord.Intents(**kwargs)
        elif hasattr(discord.Intents, intents_specifier):
            intents = getattr(discord.Intents, intents_specifier)()

        super().__init__(
            command_prefix=command_prefix or compute_command_prefix(cfg),
            description=description,
            help_command=help_command,
            intents=intents,
            **kwargs,
        )

        #: The bot's :class:`Context` subclass to use when invoking commands.
        #: Falls back to :class:`Context`.
        self.context_cls = kwargs.get("context_cls", lifesaver.commands.Context)

        if not issubclass(self.context_cls, lifesaver.commands.Context):
            raise TypeError(f"{self.context_cls} must subclass lifeaver.Context")

        #: The bot's logger.
        self.log = logging.getLogger(__name__)

        #: The Postgres pool connection.
        self.pool: Optional["asyncpg.pool.Pool"] = None

        #: A list of extensions names to reload when calling :meth:`load_all`.
        self.load_list = LoadList()

        #: A list of included extensions built into lifesaver to load.
        self._included_extensions: list[str] = INCLUDED_EXTENSIONS

        self._hot_task = None
        self._hot_reload_poller: Optional[Poller] = None
        self._hot_plug: Optional[PollerPlug] = None

    async def setup_hook(self) -> None:
        if self.config.postgres and self.pool is None:
            await self._postgres_connect()

    @overload
    def emoji(self, accessor: str, *, stringify: Literal[True] = True) -> str | None:
        ...

    @overload
    def emoji(
        self, accessor: str, *, stringify: Literal[False]
    ) -> discord.Emoji | None:
        ...

    def emoji(self, accessor: str, *, stringify: bool = False) -> str | discord.Emoji:
        """Return an emoji from the global emoji table.

        The string you pass accesses the :attr:`BotConfig.emojis` dict using
        a string of keys separated by dots. For example, ``generic.ok``
        accesses ``['generic']['ok']``.

        The global emoji table can contain both Unicode emoji and custom emoji
        IDs. If a custom emoji ID is used, :meth:`discord.Client.get_emoji` is
        called to fetch the :class:`discord.Emoji`.

        Raises
        ------
        LookupError
            The the corresponding value in the global emoji table could not be
            found.
        RuntimeError
            The custom emoji with the ID of the value in the global emoji table
            could not be found, or was an incorrect type.
        """
        try:
            emoji_string_or_id = dot_access(self.config.emojis, accessor)
        except KeyError as exc:
            raise LookupError(
                f'No such emoji "{accessor}" in global emoji table'
            ) from exc
        if not isinstance(emoji_string_or_id, str | int):
            raise RuntimeError(
                f"Expected emoji to be Unicode emoji or Discord emoji ID, but found {emoji_string_or_id!r} instead"
            )

        if isinstance(emoji_string_or_id, int):
            emoji = cast(commands.Bot, self).get_emoji(emoji_string_or_id)
        else:
            emoji = emoji_string_or_id

        if emoji is None:
            raise RuntimeError(
                f'Cannot find custom emoji with ID of {emoji_string_or_id} (while looking up "{accessor}")'
            )

        return str(emoji) if stringify else emoji

    def tick(self, affirmative: bool = True) -> str | discord.Emoji:
        """Return a tick emoji.

        Uses ``generic.yes`` and ``generic.no`` from the global emoji table.

        Raises
        ------
        RuntimeError
            Raised if the emojis weren't found.
        """
        accessor = "generic.yes" if affirmative else "generic.no"
        emoji = self.emoji(accessor)

        if not emoji:
            raise RuntimeError(f"The emoji for {accessor} wasn't found")
        return emoji

    async def _setup_hot_reload(self) -> None:
        self.log.debug("Setting up hot reload.")

        self._hot_reload_poller = Poller(Path(self.config.extensions_path))
        self.log.debug("Created poller: %r", self._hot_reload_poller)

        # setup plug, which handles the extension {un,re,}loading for us
        self._hot_plug = PollerPlug(self)

        # infinitely consume hot reload events
        self._hot_task = cast(commands.Bot, self).loop.create_task(
            self._consume_hot_reload()
        )

    async def _consume_hot_reload(self):
        assert self._hot_reload_poller is not None
        assert self._hot_plug is not None

        async for event in self._hot_reload_poller:
            await self._hot_plug.handle(event)
            self._rebuild_load_list()

    async def _postgres_connect(self):
        try:
            import asyncpg
        except ImportError:
            raise RuntimeError("Cannot connect to Postgres, asyncpg is not installed")

        self.log.debug("creating a postgres pool")
        assert isinstance(self.config.postgres, dict)
        self.pool = await asyncpg.create_pool(dsn=self.config.postgres["dsn"])
        self.log.debug("created postgres pool")

    @property
    def _is_hardcoding_load_list(self) -> list[str]:
        return bool(self.config.load_list)

    def _rebuild_load_list(self):
        if self._is_hardcoding_load_list:
            self.load_list = LoadList(self.config.load_list)
        else:
            self.load_list.build(Path(self.config.extensions_path))

    async def load_all(self, *, reload: bool = False, exclude_default: bool = False):
        """Load all extensions in the load list.

        The load list is always rebuilt first when called.
        When done, the ``load_all`` event is dispatched with the value of ``reload``.

        Parameters
        ----------
        reload
            Reload extensions instead of loading them. Uses
            :meth:`discord.ext.commands.Bot.reload_extension`.
        exclude_default
            Exclude default extensions from being loaded.
        """
        self._rebuild_load_list()

        if exclude_default:
            load_list = self.load_list
        else:
            load_list = self.load_list + self._included_extensions

        for extension_name in load_list:
            if reload:
                await self.reload_extension(extension_name)
            else:
                await self.load_extension(extension_name)

        self.dispatch("load_all", reload)

    async def on_ready(self):
        bot = cast(commands.Bot, self)
        assert bot.user is not None
        self.log.info("Ready! Logged in as %s (%d)", bot.user, bot.user.id)

        if not self._is_hardcoding_load_list and self.config.hot_reload and self._hot_plug is None:
            await self._setup_hot_reload()

    async def on_message(self, message: discord.Message):
        """The handler that handles incoming messages from Discord.

        This event automatically waits for the bot to be ready before processing
        commands. Bots are ignored according to :attr:`BotConfig.ignore_bots`
        and the context class used for commands is determined by
        :attr:`context_cls`.
        """
        await self.wait_until_ready()  # type: ignore

        if self.config.ignore_bots and message.author.bot:
            return

        ctx = await self.get_context(message, cls=self.context_cls)
        await self.invoke(ctx)


class Bot(BotBase, discord.Client):
    pass


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    pass
