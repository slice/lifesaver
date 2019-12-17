# encoding: utf-8

__all__ = ["Buttons"]

import asyncio
import typing as T

import discord

ReactionKey = T.Union[str, discord.Emoji]
ReactionHandler = T.Callable[[discord.Reaction, discord.abc.User], None]


class Buttons:
    """An abstraction over reaction buttons for messages."""

    def __init__(
        self,
        message: discord.Message,
        *,
        owner: T.Union[discord.abc.User, T.List[discord.abc.User]],
    ) -> None:
        self.message = message
        self.owner = owner

        self._task: T.Optional[asyncio.Task] = None
        self._handlers: T.Dict[ReactionKey, ReactionHandler] = {}

    def is_owner(self, user: discord.abc.User) -> bool:
        """Return whether a user is considered the/an owner."""
        if isinstance(self.owner, list):
            return user in self.owner

        return user == self.owner

    def on(self, emoji: ReactionKey, handler: ReactionHandler) -> None:
        """Register an event handler for an emoji. Only one event handler must be present for each emoji."""
        self._handlers[emoji] = handler

    def off(self, emoji: ReactionKey) -> None:
        """Delete an event handler for an emoji. Raises :class:`KeyError` if not found."""
        del self._handlers[emoji]

    def _check(self, reaction: discord.Reaction, user: discord.abc.User) -> bool:
        return reaction.message.id == self.message.id and self.is_owner(user)

    async def _dispatch(
        self, reaction: discord.Reaction, user: discord.abc.User
    ) -> None:
        handler = self._handlers.get(reaction.emoji)
        if handler:
            await discord.utils.maybe_coroutine(handler, reaction, user)

    async def _waiter(self, bot) -> None:
        while True:
            reaction, user = await bot.wait_for("reaction_add", check=self._check)
            await self._dispatch(reaction, user)

    def listen(self, bot) -> asyncio.Task:
        """Make the bot start listening for ``reaction_add`` events."""
        self._task = bot.loop.create_task(self._waiter(bot))
        return self._task

    async def add_reactions(self) -> None:
        """Add reactions for all of the attached event handlers."""
        for emoji in self._handlers:
            await self.message.add_reaction(emoji)
