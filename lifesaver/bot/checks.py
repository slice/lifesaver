import discord
from discord.ext.commands import check
from lifesaver.bot.context import LifesaverContext


def is_nsfw_or_dm():

    def _check(context: LifesaverContext):
        return (not context.guild) or (isinstance(context.channel, discord.TextChannel) and context.channel.nsfw)

    return check(_check)
