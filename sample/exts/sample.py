from discord.ext import commands
from lifesaver.bot import Cog


class Sample(Cog):
    @commands.command()
    async def sample(self, ctx):
        await ctx.send('Hello!')


def setup(bot):
    bot.add_cog(Sample(bot))
