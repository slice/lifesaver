import asyncio

from discord.ext import commands
from lifesaver.bot import Cog, Context, command, group
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.config import Config
from lifesaver.utils.formatting import codeblock


class SampleConfig(Config):
    configurable_message: str = 'Hello there'


@Cog.with_config(SampleConfig)
class Sample(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tags = AsyncJSONStorage('tags.json')

    def cog_unload(self):
        print('Calling super unload:', super().cog_unload)
        super().cog_unload()
        print('My unload.')

    @group()
    async def samplegroup(self, ctx: Context):
        pass

    @command()
    async def message(self, ctx: Context):
        await ctx.send(self.config.configurable_message)

    @samplegroup.command(typing=True)
    async def subcommand(self, ctx: Context):
        await asyncio.sleep(5)
        await ctx.send('yo!')

    @command()
    async def pages_example(self, ctx: Context):
        from random import random
        for _ in range(150):
            ctx += str(random())
        await ctx.send_pages()

    @command()
    async def sample(self, ctx: Context):
        """A sample command."""
        await ctx.send('Hello!')

    @command()
    async def source(self, ctx: Context, command):
        """View the source of a command."""
        cmd = ctx.bot.get_command(command)
        if not cmd:
            await ctx.send('No such command.')
            return
        from inspect import getsource
        await ctx.send(codeblock(getsource(cmd.callback), lang='py'))

    @Cog.every(10, wait_until_ready=True)
    async def scheduled(self):
        print('Scheduled function.')

    @group(invoke_without_command=True)
    async def tag(self, ctx: Context, *, key):
        """Tag management commands."""
        tag = self.tags.get(key)
        if not tag:
            await ctx.send('No such tag.')
        else:
            await ctx.send(tag)

    @tag.command()
    async def list(self, ctx: Context):
        """Lists all tags."""
        tags = self.tags.all().keys()
        await ctx.send(f'{len(tags)}: {", ".join(tags)}')

    @tag.command(aliases=['create'])
    async def make(self, ctx: Context, key: commands.clean_content, *, value: commands.clean_content):
        """Creates a tag."""
        if key in self.tags:
            await ctx.send('Tag already exists.')
            return
        await self.tags.put(key, value)
        await ctx.ok()


def setup(bot):
    bot.add_cog(Sample(bot))
