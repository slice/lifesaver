# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2017 - 2018 slice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
