from lifesaver.bot import Cog, command


class Health(Cog):
    @command()
    async def ping(self, ctx):
        """Pings the bot."""
        ping_time = round(ctx.bot.latency * 1000, 2)
        await ctx.send(f'Pong! Heartbeat latency: `{ping_time}ms`')


def setup(bot):
    bot.add_cog(Health(bot))
