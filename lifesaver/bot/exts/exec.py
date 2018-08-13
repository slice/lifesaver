"""

Some code taken from: https://github.com/b1naryth1ef/b1nb0t/

=================================================================================

MIT License

Copyright (c) 2017 - 2018 slice
Copyright (c) 2018 FrostLuma
Copyright (c) 2015 Rapptz

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
import asyncio
import logging
import textwrap
import traceback
from contextlib import suppress
from io import StringIO
from typing import Any, Callable, Dict, List, TypeVar, Union

import discord
from discord.ext import commands
from discord.ext.commands import is_owner
from lifesaver.bot import Cog, Context, command
from lifesaver.utils import codeblock
from lifesaver.utils.timing import Timer

log = logging.getLogger(__name__)
IMPLICIT_RETURN_BLACKLIST = {
    # statements
    'assert', 'del', 'with',

    # imports
    'from', 'import',

    # control flow
    'break', 'continue', 'pass', 'raise', 'return', 'yield'
}


def code_in_codeblock(arg: str) -> str:
    result = arg

    lines = result.splitlines()

    # remove codeblock ticks
    if result.startswith('```') and result.endswith('```'):
        if len(lines) == 1:
            result = lines[0][3:-3]
        else:
            result = '\n'.join(result.split('\n')[1:-1])

    # remove inline code ticks
    result = result.strip('` \n')

    return result


def create_environment(cog: 'Exec', ctx: Context) -> Dict[Any, Any]:
    async def upload(file_name: str) -> discord.Message:
        """Shortcut to upload a file."""
        with open(file_name, 'rb') as fp:
            return await ctx.send(file=discord.File(fp))

    def better_dir(*args, **kwargs) -> List[str]:
        """dir(), but without magic methods."""
        return [n for n in dir(*args, **kwargs) if not n.endswith('__') and not n.startswith('__')]

    def get_member(specifier: Union[int, str]) -> discord.Member:
        if not ctx.guild:
            raise RuntimeError('Cannot use member grabber in a DM context.')

        def _finder(member: discord.Member) -> bool:
            return any([
                member.id == specifier,
                # name#discrim
                str(member) == specifier,
                member.display_name == specifier,
                member.name == specifier,
            ])

        return discord.utils.find(_finder, ctx.guild.members)

    T = TypeVar('T')

    def grabber(lst: List[T]) -> Callable[[int], T]:
        """Returns a function that, when called, grabs an item by ID from a list of objects with an ID."""

        def _grabber_function(thing_id: int) -> T:
            return discord.utils.get(lst, id=thing_id)

        return _grabber_function

    env = {
        # shortcuts
        'bot': ctx.bot,
        'ctx': ctx,
        'msg': ctx.message,
        'guild': ctx.guild,
        'channel': ctx.channel,
        'me': ctx.message.author,
        'cog': cog,

        # modules
        'discord': discord,
        'asyncio': asyncio,
        'commands': commands,
        'command': commands.command,
        'group': commands.group,

        # utilities
        '_get': discord.utils.get,
        '_find': discord.utils.find,
        '_upload': upload,
        '_send': ctx.send,

        # grabbers
        '_g': grabber(ctx.bot.guilds),
        '_u': grabber(ctx.bot.users),
        '_c': ctx.bot.get_channel,
        '_m': get_member,

        # last result
        '_': cog.last_result,
        'dir': better_dir,
    }

    # add globals to environment
    env.update(globals())

    return env


def format_syntax_error(e: SyntaxError) -> str:
    """Formats a SyntaxError."""
    if e.text is None:
        return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
    # display a nice arrow
    return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)


class Exec(Cog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = set()
        self.last_result = None

    def __unload(self):
        self.cancel_sessions()

    async def execute(self, ctx: Context, code: str):
        log.info('Eval: %s', code)

        env = create_environment(self, ctx)

        def compile_code(to_compile):
            wrapped_code = 'async def _wrapped():\n' + textwrap.indent(to_compile, ' ' * 4)
            exec(compile(wrapped_code, '<exec>', mode='exec'), env)

        # we'll try to add an implicit return. if we succeed, we set this flag
        # to avoid running the code twice
        compiled = False

        try:
            lines = code.splitlines()
            if not any(lines[-1].startswith(word) for word in IMPLICIT_RETURN_BLACKLIST):
                lines[-1] = 'return ' + lines[-1]
                compile_code('\n'.join(lines))
                compiled = True
        except SyntaxError:
            # failed to implicitly return, just bail. we'll recompile the code
            # without our implicit return
            pass

        if not compiled:
            try:
                compile_code(code)
            except SyntaxError as error:
                with suppress(discord.HTTPException):
                    await ctx.message.add_reaction('\N{DOUBLE EXCLAMATION MARK}')
                await ctx.send(format_syntax_error(error))
                return

        # grab the defined function
        func = env['_wrapped']

        task = self.bot.loop.create_task(func())
        self.sessions.add(task)

        async def late_indicator():
            await asyncio.sleep(3)
            with suppress(discord.HTTPException):
                await ctx.message.add_reaction('\N{HOURGLASS WITH FLOWING SAND}')
                await ctx.message.add_reaction('\N{HOCHO}')

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == ctx.message.id and reaction.emoji == '\N{HOCHO}'

            while True:
                await self.bot.wait_for('reaction_add', check=check)
                self.log.debug('cancelling task: %s', task)
                task.cancel()

        late_task = self.bot.loop.create_task(late_indicator())

        try:
            with Timer() as timer:
                await asyncio.gather(task)
        except asyncio.CancelledError:
            with suppress(discord.HTTPException):
                await ctx.message.add_reaction('\N{OCTAGONAL SIGN}')
            return
        except Exception:
            with suppress(discord.HTTPException):
                await ctx.message.add_reaction('\N{DOUBLE EXCLAMATION MARK}')

            await ctx.send(codeblock(traceback.format_exc(limit=7)))
            return
        finally:
            self.sessions.remove(task)
            if not late_task.done():
                late_task.cancel()

        with suppress(discord.HTTPException):
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

        result = task.result()

        if result is not None:
            self.last_result = result

        representation = repr(result)
        marker = ''

        if isinstance(result, str):
            representation = result
            marker = ' (string)'

        message = f'Took {timer} to execute.{marker}\n' + codeblock(representation)

        if len(message) > 2000:
            file = discord.File(fp=StringIO(message), filename='result.txt')
            try:
                await ctx.send(file=file)
            except discord.HTTPException as error:
                await ctx.send(f'Cannot send result: `{error}`')
        else:
            await ctx.send(message)

    @command(name='eval', aliases=['exec', 'debug'])
    @is_owner()
    async def _eval(self, ctx, *, code: code_in_codeblock):  # type: ignore
        """Evaluates Python code in realtime."""
        await self.execute(ctx, code)

    @command()
    @is_owner()
    async def cancel(self, ctx):
        """Cancels running code."""
        self.cancel_sessions()
        await ctx.ok()

    def cancel_sessions(self):
        for task in self.sessions:
            task.cancel()


def setup(bot):
    bot.add_cog(Exec(bot))
