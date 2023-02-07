# encoding: utf-8

from discord.ext import commands

import lifesaver


class Health(lifesaver.Cog):
    @lifesaver.command(aliases=["p"])
    @commands.cooldown(1, 1, type=commands.BucketType.guild)
    async def ping(self, ctx: lifesaver.commands.Context):
        """Check if the bot is responding."""
        await ctx.ok("\N{TABLE TENNIS PADDLE AND BALL}")


async def setup(bot):
    await bot.add_cog(Health(bot))
