from discord.ext import commands
from discord.ext.commands import command

from lifesaver.bot import Cog, Context


class Admin(Cog):
    """A cog that provides commands related to administration of the bot."""

    @command()
    @commands.is_owner()
    async def reload(self, ctx: Context):
        """Reloads all extensions."""
        try:
            ctx.bot.load_all(unload_first=True)
        except Exception:
            await ctx.send('An error has occurred while reloading.')
            self.log.exception('Cog load error:')
        else:
            await ctx.ok()

    @command()
    @commands.is_owner()
    async def unload(self, ctx: Context, ext):
        """Unloads an extension."""
        ctx.bot.unload_extension(ext)
        await ctx.ok()

    @command(aliases=['shutdown'])
    @commands.is_owner()
    async def die(self, ctx: Context):
        """Kills the bot."""
        await ctx.send('\N{WAVING HAND SIGN} Bye!')
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
