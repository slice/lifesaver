from discord.ext import commands
from discord.ext.commands import group
from lifesaver.bot import Cog, command
from lifesaver.bot.storage import AsyncJSONStorage


class Sample(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tags = AsyncJSONStorage('tags.json')

    def __unload(self):
        print('Original unload.')

    @command()
    async def sample(self, ctx):
        """ A sample command. """
        await ctx.send('Hello!')

    @Cog.every(10, wait_until_ready=True)
    async def scheduled(self):
        pass

    @group(invoke_without_command=True)
    async def tag(self, ctx, *, key):
        """ Tag management commands. """
        tag = self.tags.get(key)
        if not tag:
            await ctx.send('No such tag.')
        else:
            await ctx.send(tag)

    @tag.command()
    async def list(self, ctx):
        """ Lists all tags. """
        tags = self.tags.all().keys()
        await ctx.send(f'{len(tags)}: {", ".join(tags)}')

    @tag.command(aliases=['create'])
    async def make(self, ctx, key: commands.clean_content, *, value: commands.clean_content):
        """ Creates a tag. """
        if key in self.tags:
            await ctx.send('Tag already exists.')
            return
        await self.tags.put(key, value)
        await ctx.ok()


def setup(bot):
    bot.add_cog(Sample(bot))
