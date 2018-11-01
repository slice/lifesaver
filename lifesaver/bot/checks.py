# encoding: utf-8

import discord
from discord.ext.commands import check


def is_nsfw_or_dm():
    """A check that passes when the current command context is in a NSFW channel or a DM."""

    def predicate(ctx):
        return not ctx.guild or (isinstance(ctx.channel, discord.TextChannel) and ctx.channel.nsfw)

    return check(predicate)
