# encoding: utf-8

import asyncio
import datetime
import secrets
import sys
import time
from collections import OrderedDict

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


class Errors(lifesaver.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.insects = Storage("./insects.json")
        self.insect_creation_lock = asyncio.Lock()

        # clobber original on_error because it's a faux-event
        self._original_on_error = bot.on_error
        bot.on_error = self.on_error

    #: Errors to ignore.
    ignored_errors = {
        # Silently ignore ratelimit violations.
        commands.CommandOnCooldown,
        # Silently ignore other check failures.
        commands.CheckFailure,
        # Silently ignore command not found errors.
        commands.CommandNotFound,
    }

    #: Default error handlers.
    error_handlers = OrderedDict(
        [
            (commands.TooManyArguments, ("Too many arguments.", False)),
            (commands.BotMissingPermissions, ("Permissions error", True)),
            (commands.MissingPermissions, ("Permissions error", True)),
            (
                commands.NoPrivateMessage,
                ("You can't do that in a direct message.", False),
            ),
            (commands.NotOwner, ("Only of the owner of this bot can do that.", False)),
            (commands.DisabledCommand, ("This command has been disabled.", False)),
            (commands.UserInputError, ("User input error", True)),
            (commands.CheckFailure, ("Permissions error", True)),
            (
                lifesaver.commands.SubcommandInvocationRequired,
                (
                    "You need to specify a subcommand to run. Run `{prefix}help {command}` for help.",
                    False,
                ),
            ),
        ]
    )

    def cog_unload(self):
        super().cog_unload()

        # restore original on_error
        self.bot.on_error = self._original_on_error

    def make_insect_id(self) -> str:
        return secrets.token_hex(6)

    async def create_insect(self, error: BaseException) -> str:
        """Create and save an insect object, returning its ID."""
        async with self.insect_creation_lock:
            insects = self.insects.get("insects", [])

            insect_id = self.make_insect_id()
            insects.append(
                {
                    "id": insect_id,
                    "creation_time": time.time(),
                    "traceback": format_traceback(error, hide_paths=True),
                }
            )

            await self.insects.put("insects", insects)

        return insect_id

    @lifesaver.group(hidden=True, hollow=True)
    @commands.is_owner()
    async def errors(self, ctx: lifesaver.commands.Context):
        """Manages errors."""

    @errors.command(name="recent")
    async def errors_recent(self, ctx: lifesaver.commands.Context, amount: int = 5):
        """Shows recent insects."""
        all_insects = self.insects.get("insects", [])

        if not all_insects:
            await ctx.send("There are no insects.")
            return

        recent_insects = sorted(
            all_insects[-amount:],
            key=lambda insect: insect["creation_time"],
            reverse=True,
        )

        def format_insect(insect):
            ago = human_delta(
                datetime.datetime.utcfromtimestamp(insect["creation_time"])
            )
            summary = summarize_traceback(insect["traceback"])
            return f'\N{BUG} **`{insect["id"]}`** `{summary}` ({ago})'

        embed = discord.Embed(
            title="Recent Insects",
            color=discord.Color.red(),
            description="\n".join(map(format_insect, recent_insects)),
        )
        embed.set_footer(text=f"{pluralize(insect=len(all_insects))} in total.")

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Too much information to display.")

    @errors.command(name="view", aliases=["show", "info"])
    async def errors_view(self, ctx: lifesaver.commands.Context, insect_id):
        """Views an error by insect ID."""
        all_insects = self.insects.get("insects", [])
        insect = discord.utils.find(
            lambda insect: insect["id"] == insect_id, all_insects
        )

        if not insect:
            await ctx.send("There is no insect with that ID.")
            return

        created = datetime.datetime.utcfromtimestamp(insect["creation_time"])
        ago = human_delta(created)

        embed = discord.Embed(
            title=f"Insect {insect_id}",
            color=discord.Color.red(),
            description=codeblock(insect["traceback"], lang="py"),
        )
        embed.add_field(
            name="Created", value=f"{created} UTC ({ago} ago)", inline=False
        )
        await ctx.send(embed=embed)

    @errors.command(name="throw", hidden=True)
    async def errors_throw(self, ctx: lifesaver.commands.Context, *, message="!"):
        """Throws an error. Useful for debugging."""
        raise RuntimeError(f"Intentional error: {message}")

    async def on_error(self, event, *args, **kwargs):
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
    async def on_command_error(self, ctx: lifesaver.commands.Context, error: BaseException):
        ignored_errors = getattr(ctx.bot, "ignored_errors", [])
        filtered_handlers = OrderedDict(
            (key, value)
            for (key, value) in self.error_handlers.items()
            if key not in ignored_errors
        )

        if isinstance(error, commands.BadArgument):
            if "failed for parameter" in str(error) and error.__cause__ is not None:
                self.log.error(
                    "Generic check error. %s", format_traceback(error.__cause__)
                )
            await ctx.send(f"Bad argument. {error}")
            return

        for (
            error_type,
            (message_format, do_append_message),
        ) in filtered_handlers.items():
            if not isinstance(error, error_type):
                continue

            assert ctx.command is not None
            message = message_format.format(
                prefix=ctx.prefix, command=ctx.command.qualified_name
            )

            if do_append_message:
                await ctx.send(f"{message}: {error}")
            else:
                await ctx.send(message)

            return

        if type(error) in self.ignored_errors:
            return

        self.log.error("Fatal error. %s", format_traceback(error))
        insect_id = await self.create_insect(error)
        await ctx.send(f"Something went wrong. \N{BUG} `{insect_id}`")


async def setup(bot):
    await bot.add_cog(Errors(bot))
