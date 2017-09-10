from discord.ext import commands
from lifesaver.bot import Cog
from discord.ext.commands import command

from lifesaver.bot.exts.errors import get_traceback
from lifesaver.utils import codeblock


class Admin(Cog):
    """A cog that provides commands related to administration of the bot."""

    @command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reloads all extensions."""
        try:
            ctx.bot.load_all(unload_first=True)
        except Exception as exc:
            error = codeblock(get_traceback(exc), lang='py')
            await ctx.send(error)
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @command()
    @commands.is_owner()
    async def unload(self, ctx, ext):
        """Unloads an extension."""
        ctx.bot.unload_extension(ext)
        await ctx.send('\N{OK HAND SIGN}')

    @command(aliases=['shutdown'])
    @commands.is_owner()
    async def die(self, ctx):
        """Kills the bot."""
        await ctx.send('\N{WAVING HAND SIGN} Bye!')
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
