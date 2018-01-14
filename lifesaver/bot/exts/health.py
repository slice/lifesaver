from discord.ext.commands import command

from lifesaver.bot import Cog, Context


class Health(Cog):
    @command()
    async def ping(self, ctx: Context):
        """Pings the bot."""
        ping_time = round(ctx.bot.latency * 1000, 2)
        await ctx.send(f'Pong! Heartbeat latency: `{ping_time}ms`')


def setup(bot):
    bot.add_cog(Health(bot))
