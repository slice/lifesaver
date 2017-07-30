from discord.ext import commands
from lifesaver.bot import Cog


class Admin(Cog):
    """A cog that provides commands related to administration of the bot."""

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reloads all extensions."""
        try:
            ctx.bot.load_all(unload_first=True)
        except Exception as exc:
            await ctx.send(f'Error!\n```py\n{exc}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(aliases=['shutdown', 'poweroff'])
    @commands.is_owner()
    async def die(self, ctx):
        """Kills the bot."""
        await ctx.send('\N{WAVING HAND SIGN}')
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
