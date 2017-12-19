import discord
from lifesaver.bot import Cog, command


class BreadFeed(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribers = []

    @Cog.every(5)
    async def publish_to_subscribers(self):
        for subscriber in self.subscribers:
            user = self.bot.get_user(subscriber)

            if not user:
                continue

            try:
                await user.send('\N{BREAD}')
            except discord.HTTPException:
                self.log.warning('Failed to send bread to %d.', user.id)

    @command()
    async def sendmebread(self, ctx):
        """Want bread?"""
        self.subscribers.append(ctx.author.id)
        await ctx.ok()

    @command()
    async def ihatebread(self, ctx):
        """Hate bread?"""
        self.subscribers.remove(ctx.author.id)
        await ctx.ok()


def setup(bot):
    bot.add_cog(BreadFeed(bot))
