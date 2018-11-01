# encoding: utf-8

from discord.ext import commands

from lifesaver.bot import command, Cog, Context
from lifesaver.utils import shell, escape_backticks


class Admin(Cog):
    """A cog that provides commands related to administration of the bot."""

    @command(aliases=['r'])
    @commands.is_owner()
    async def reload(self, ctx: Context):
        """Reloads all extensions."""
        try:
            ctx.bot.load_all(unload_first=True)
        except Exception:
            await ctx.ok('\N{DOUBLE EXCLAMATION MARK}')
            self.log.exception('Cog load error:')
        else:
            await ctx.ok()

    @command(name='shell', aliases=['sh'])
    @commands.is_owner()
    async def _shell(self, ctx: Context, *, command):
        """Runs a shell command on the system."""
        output = await shell(command)
        for line in output.split('\n'):
            ctx += escape_backticks(line)
        await ctx.send_pages()

    @command()
    @commands.is_owner()
    async def unload(self, ctx: Context, ext):
        """Unloads an extension."""
        ctx.bot.unload_extension(ext)
        await ctx.ok()

    @command()
    @commands.is_owner()
    async def load(self, ctx: Context, ext):
        """Loads an extension."""
        ctx.bot.load_extension(ext)
        await ctx.ok()

    @command(aliases=['shutdown'])
    @commands.is_owner()
    async def die(self, ctx: Context):
        """Kills the bot."""
        await ctx.send('\N{WAVING HAND SIGN} Bye!')
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
