# encoding: utf-8

import asyncio
import datetime
import json
import secrets
import sys
import dataclasses
from dataclasses import field
from collections import OrderedDict
from typing import NamedTuple, Any

import discord
from discord.ext import commands

import lifesaver
from lifesaver.bot.storage import Storage
from lifesaver.utils import (
    codeblock,
    format_traceback,
    human_delta,
    pluralize,
    truncate,
)


def summarize_traceback(traceback: str, *, max_len: int = 30) -> str:
    last_line = traceback.splitlines()[-1]
    last_line = last_line.replace(
        "discord.ext.commands.errors.CommandInvokeError: Command raised an exception: ",
        "",
    )
    return truncate(last_line, max_len)


@dataclasses.dataclass
class Insect:
    traceback: str
    id: str = field(default_factory=lambda: secrets.token_hex(6))
    creation_time: datetime.datetime = field(default_factory=discord.utils.utcnow)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Insect):
            return other.id == self.id
        return NotImplemented

    def format(self) -> str:
        summary = summarize_traceback(self.traceback)
        return f'\N{BUG} **`{self.id}`** `{summary}` {discord.utils.format_dt(self.creation_time, "R")}'


class ErrorHandler(NamedTuple):
    message: str
    append_original_message: bool = False


class InsectsEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Insect):
            insect_dict = dataclasses.asdict(o)
            insect_dict["creation_time"] = insect_dict["creation_time"].timestamp()
            return insect_dict
        return json.JSONEncoder.default(self, object)


def insect_object_hook(dictionary: dict[str, Any]) -> Any:
    if "traceback" in dictionary:
        return Insect(
            traceback=dictionary["traceback"],
            id=dictionary["id"],
            creation_time=datetime.datetime.fromtimestamp(
                dictionary["creation_time"], tz=datetime.timezone.utc
            ),
        )
    return dictionary


class Errors(lifesaver.Cog):
    def __init__(self, bot: lifesaver.Bot):
        super().__init__(bot)
        self.insects = Storage[list[Insect]](
            "./insects.json", encoder=InsectsEncoder, object_hook=insect_object_hook
        )
        self.insect_creation_lock = asyncio.Lock()

        # clobber original on_error because it's a faux-event
        self._original_on_error = bot.on_error
        bot.on_error = self.replacement_on_error

    #: Errors to silently ignore.
    silenced_errors = {
        # Silently ignore ratelimit violations.
        commands.CommandOnCooldown,
        # Silently ignore other check failures.
        commands.CheckFailure,
        # Silently ignore command not found errors.
        commands.CommandNotFound,
    }

    #: Default error handlers.
    error_handlers = {
        commands.TooManyArguments: ErrorHandler("Too many inputs."),
        commands.BotMissingPermissions: ErrorHandler(
            "The bot doesn't have permission to do that", append_original_message=True
        ),
        commands.MissingPermissions: ErrorHandler(
            "You don't have permission to do that", append_original_message=True
        ),
        commands.NoPrivateMessage: ErrorHandler(
            "You can't do that in Direct Messages."
        ),
        commands.NotOwner: ErrorHandler("Only the owner of this bot can do that."),
        commands.DisabledCommand: ErrorHandler(
            "This command is currently unavailable."
        ),
        commands.UserInputError: ErrorHandler(
            "Something was wrong with your input", append_original_message=True
        ),
        commands.CheckFailure: ErrorHandler(
            "You can't do that", append_original_message=True
        ),
        commands.BadArgument: ErrorHandler(
            "Something was wrong with your input", append_original_message=True
        ),
        lifesaver.commands.SubcommandInvocationRequired: ErrorHandler(
            "You need to run a subcommand. Type `{prefix}help {command}` for help."
        ),
    }

    def cog_unload(self):
        super().cog_unload()

        # restore original on_error
        self.bot.on_error = self._original_on_error

    async def create_insect(self, error: BaseException) -> str:
        """Create and save an insect object, returning its ID."""
        async with self.insect_creation_lock:
            insects = self.insects.get("insects", [])
            insect = Insect(traceback=format_traceback(error, shorten_paths=True))
            insects.append(insect)
            await self.insects.put("insects", insects)

        return insect.id

    @lifesaver.group(hidden=True, hollow=True)
    @commands.is_owner()
    async def errors(self, ctx: lifesaver.Context):
        """Manages errors."""

    @errors.command(name="recent")
    async def errors_recent(self, ctx: lifesaver.Context, amount: int = 5):
        """Shows recent insects."""
        all_insects = self.insects.get("insects", [])

        if not all_insects:
            await ctx.send("There are no insects.")
            return

        recent_n_insects = sorted(
            all_insects[-amount:],
            key=lambda insect: insect.creation_time,
            reverse=True,
        )

        embed = discord.Embed(
            title="Recent Insects",
            color=discord.Color.red(),
            description="\n".join(insect.format() for insect in recent_n_insects),
        )
        embed.set_footer(text=pluralize(insect=len(all_insects)))

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Too much information to display.")

    @errors.command(name="view", aliases=["show", "info"])
    async def errors_view(self, ctx: lifesaver.commands.Context, insect_id: str):
        """Views an error by insect ID."""
        all_insects = self.insects.get("insects", [])
        insect = discord.utils.find(lambda insect: insect.id == insect_id, all_insects)

        if not insect:
            await ctx.send("There is no insect with that ID.")
            return

        embed = discord.Embed(
            title=f"Insect `{insect_id}`",
            color=discord.Color.red(),
            description=codeblock(insect.traceback, lang="py"),
        )
        embed.add_field(
            name="Occurred",
            value=discord.utils.format_dt(insect.creation_time, "R"),
            inline=False,
        )
        await ctx.send(embed=embed)

    @errors.command(name="throw", hidden=True)
    async def errors_throw(self, ctx: lifesaver.Context, *, message: str = "!"):
        """Intentionally creates a runtime error."""
        raise RuntimeError(f"Intentional error: {message}")

    async def replacement_on_error(self, event: str, *args: Any, **kwargs: Any):
        _, value, _ = sys.exc_info()

        if value is None:
            self.log.error("Fatal error occurred, but exc_info returned None.")
            return

        self.log.error(
            "Fatal error in %s (args=%r, kwargs=%r). %s",
            event,
            args,
            kwargs,
            format_traceback(value),
        )

        await self.create_insect(value)

    @lifesaver.Cog.listener()
    async def on_command_error(
        self, ctx: lifesaver.commands.Context, error: BaseException
    ):
        if isinstance(error, commands.BadArgument):
            # If the error contains a generic message, it probably failed in
            # a way we weren't anticipating (because ideally, we'd give a
            # better error message). Log the conversion failure.
            if "failed for parameter" in str(error) and error.__cause__ is not None:
                self.log.error(
                    "Generic conversion failed. %s", format_traceback(error.__cause__)
                )

        ignored_errors = getattr(ctx.bot, "ignored_errors", [])

        for (
            error_type,
            (message_format, append_original_message),
        ) in self.error_handlers.items():
            if not isinstance(error, error_type) or error_type in ignored_errors:
                continue

            assert ctx.command is not None
            message = message_format.format(
                prefix=ctx.prefix, command=ctx.command.qualified_name
            )

            await ctx.send(
                f"{message}: {error}" if append_original_message else message
            )
            return

        if type(error) in self.silenced_errors:
            return

        self.log.error("Fatal error. %s", format_traceback(error))
        insect_id = await self.create_insect(error)
        await ctx.send(f"Something went wrong! \N{BUG} `{insect_id}`")


async def setup(bot: lifesaver.Bot):
    await bot.add_cog(Errors(bot))
