import asyncio

from discord.ext import commands
import lifesaver
from lifesaver.bot.storage import AsyncJSONStorage
from lifesaver.config import Config
from lifesaver.utils.formatting import codeblock


class SampleConfig(Config):
    configurable_message: str = 'Hello there'


@lifesaver.Cog.with_config(SampleConfig)
class Sample(lifesaver.Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = AsyncJSONStorage('tags.json')

    def cog_unload(self):
        print('Calling super unload:', super().cog_unload)
        super().cog_unload()
        print('My unload.')

    @lifesaver.command()
    async def long_help(self, ctx: lifesaver.commands.Context):
        """A command with a long help message.

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin
        ultricies nulla sed sapien varius posuere. Suspendisse volutpat
        lobortis ligula sit amet feugiat. Duis lobortis turpis id diam porta,
        eget egestas dui posuere. Maecenas scelerisque efficitur nunc. Ut ac
        sem placerat, placerat libero sit amet, consectetur tellus. Vivamus
        venenatis efficitur leo, at sollicitudin odio efficitur vel. Orci
        varius natoque penatibus et magnis dis parturient montes, nascetur
        ridiculus mus. Praesent porta elementum dolor et euismod. Etiam et
        ullamcorper elit, quis bibendum tellus. Vivamus mattis ipsum ac gravida
        efficitur. Vestibulum et finibus ipsum. Vestibulum lorem lectus,
        rhoncus ac odio in, maximus iaculis lacus. Ut a volutpat nisl. Integer
        a fringilla arcu. Cras condimentum maximus magna at viverra.
        Pellentesque habitant morbi tristique senectus et netus et malesuada
        fames ac turpis egestas.

        Pellentesque rutrum lectus eget consectetur varius. Suspendisse
        facilisis condimentum nisi sit amet ultrices. Suspendisse non ipsum id
        metus volutpat venenatis id sed odio. Suspendisse eu fringilla ante,
        quis tempus arcu. Vivamus lacus leo, facilisis et viverra et,
        ullamcorper eget dui. Proin eleifend bibendum enim, sit amet congue
        justo molestie eget. Proin in felis quis nisi efficitur lacinia non nec
        enim. Proin vel sapien vel ipsum commodo venenatis. Morbi ornare porta
        dui, eget varius turpis fermentum id. Cras nec nulla elit. Morbi sit
        amet nunc lobortis, porttitor odio nec, malesuada sem. Suspendisse
        efficitur malesuada viverra. Duis eleifend, felis a tristique faucibus,
        neque odio faucibus purus, ac lacinia quam orci quis leo.
        """

    @lifesaver.group()
    async def sample_group(self, ctx: lifesaver.commands.Context):
        """I am a group."""

    @sample_group.command(typing=True)
    async def subcommand_two(self, ctx: lifesaver.commands.Context):
        """I am a second subcommand."""
        await asyncio.sleep(5)
        await ctx.send('yo!')

    @sample_group.command(typing=True)
    async def subcommand(self, ctx: lifesaver.commands.Context):
        """I am a subcommand."""
        await asyncio.sleep(5)
        await ctx.send('yo!')

    @lifesaver.command()
    async def message(self, ctx: lifesaver.commands.Context):
        """Sends the configurable message."""
        await ctx.send(self.config.configurable_message)

    @lifesaver.command()
    async def pages_example(self, ctx: lifesaver.commands.Context):
        """A demonstration of `ctx +=`."""
        from random import random
        for _ in range(150):
            ctx += str(random())
        await ctx.send_pages()

    @lifesaver.command()
    async def sample(self, ctx: lifesaver.commands.Context):
        """A sample command."""
        await ctx.send('Hello!')

    @lifesaver.command()
    async def source(self, ctx: lifesaver.commands.Context, command):
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

    @lifesaver.group(invoke_without_command=True)
    async def tag(self, ctx: lifesaver.commands.Context, *, key):
        """Tag management commands."""
        tag = self.tags.get(key)
        if not tag:
            await ctx.send('No such tag.')
        else:
            await ctx.send(tag)

    @tag.command()
    async def list(self, ctx: lifesaver.commands.Context):
        """Lists all tags."""
        tags = self.tags.all().keys()
        await ctx.send(f'{len(tags)}: {", ".join(tags)}')

    @tag.command(aliases=['create'])
    async def make(
        self,
        ctx: lifesaver.commands.Context,
        key: commands.clean_content,
        *,
        value: commands.clean_content,
    ):
        """Creates a tag."""
        if key in self.tags:
            await ctx.send('Tag already exists.')
            return
        await self.tags.put(key, value)
        await ctx.ok()


def setup(bot):
    bot.add_cog(Sample(bot))
