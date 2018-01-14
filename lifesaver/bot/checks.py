import discord
from discord.ext.commands import check

from lifesaver.bot import Context


def is_nsfw_or_dm():
    """A check that passes when the current command context is in a NSFW channel, or a DM."""

    def _check(context: Context):
        return (not context.guild) or (isinstance(context.channel, discord.TextChannel) and context.channel.nsfw)

    return check(_check)
