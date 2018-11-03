# encoding: utf-8

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

__all__ = ['grabber', 'code_in_codeblock', 'create_environment', 'format_syntax_error', 'Exec', 'setup',
           'IMPLICIT_RETURN_BLACKLIST']

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
from lifesaver.bot import Cog, Context, group
from lifesaver.utils import codeblock
from lifesaver.utils.timing import Timer

log = logging.getLogger(__name__)
IMPLICIT_RETURN_BLACKLIST = {
    # Statements:
    'assert', 'del', 'with',

    # Imports:
    'from', 'import',

    # Control flow:
    'break', 'continue', 'pass', 'raise', 'return', 'yield'
}

T = TypeVar('T')


def grabber(lst: List[T]) -> Callable[[int], T]:
    """Construct a grabber by ID function from a list."""

    def _grabber_function(thing_id: int) -> T:
        return discord.utils.get(lst, id=thing_id)

    return _grabber_function


def code_in_codeblock(arg: str) -> str:
    """Extract code from a codeblock or inline code."""
    result = arg

    lines = result.splitlines()

    # Code block.
    if result.startswith('```') and result.endswith('```'):
        if len(lines) == 1:
            result = lines[0][3:-3]
        else:
            result = '\n'.join(result.split('\n')[1:-1])

    # Inline code.
    result = result.strip('` \n')

    return result


def create_environment(cog: 'Exec', ctx: Context) -> Dict[Any, Any]:
    async def upload(file_name: str) -> discord.Message:
        """Upload a file by filename."""
        with open(file_name, 'rb') as fp:
            return await ctx.send(file=discord.File(fp))

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

    env = {
        # Shortcuts:
        'bot': ctx.bot,
        'ctx': ctx,
        'msg': ctx.message,
        'guild': ctx.guild,
        'channel': ctx.channel,
        'me': ctx.message.author,
        'cog': cog,

        # Modules:
        'discord': discord,
        'asyncio': asyncio,
        'commands': commands,
        'command': commands.command,
        'group': commands.group,

        # Utilities:
        '_get': discord.utils.get,
        '_find': discord.utils.find,
        '_upload': upload,

        # Grabbers:
        '_g': grabber(ctx.bot.guilds),
        '_u': grabber(ctx.bot.users),
        '_c': ctx.bot.get_channel,
        '_m': get_member,

        # Last result:
        '_': cog.last_result,
    }

    # add globals to environment
    env.update(globals())

    return env


def format_syntax_error(e: SyntaxError) -> str:
    """Format a SyntaxError nicely."""
    if e.text is None:
        return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
    # Display a nice arrow:
    return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)


class Exec(Cog):
    """A cog that allows for lenient runtime evaluation of Python code."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #: A list of currently executing sessions.
        self.sessions = set()

        #: The result of the last evaluation.
        self.last_result = None

    def __unload(self):
        self.cancel_sessions()

    async def execute(self, ctx: Context, code: str):
        log.info('Eval: %s', code)

        env = create_environment(self, ctx)

        def compile_code(to_compile):
            wrapped_code = 'async def _wrapped():\n' + textwrap.indent(to_compile, ' ' * 4)
            exec(compile(wrapped_code, '<exec>', mode='exec'), env)

        # We'll try to add an implicit return.  If we succeed, we set this flag
        # to avoid running the code twice.
        compiled = False

        try:
            lines = code.splitlines()
            if not any(lines[-1].startswith(word) for word in IMPLICIT_RETURN_BLACKLIST):
                lines[-1] = 'return ' + lines[-1]
                compile_code('\n'.join(lines))
                compiled = True
        except SyntaxError:
            # Failed to implicitly return, just bail.  We'll recompile the code
            # without our implicit return.
            pass

        if not compiled:
            try:
                compile_code(code)
            except SyntaxError as error:
                with suppress(discord.HTTPException):
                    await ctx.message.add_reaction(ctx.emoji('exec.error'))
                await ctx.send(format_syntax_error(error))
                return

        # grab the defined function
        func = env['_wrapped']

        task = self.bot.loop.create_task(func())
        self.sessions.add(task)

        async def late_indicator():
            await asyncio.sleep(3)

            kill_emoji = ctx.emoji('exec.kill')

            with suppress(discord.HTTPException):
                await ctx.message.add_reaction(kill_emoji)

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == ctx.message.id and reaction.emoji == kill_emoji

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
                await ctx.message.add_reaction(ctx.emoji('exec.cancelled'))
            return
        except Exception:
            with suppress(discord.HTTPException):
                await ctx.message.add_reaction(ctx.emoji('exec.error'))

            await ctx.send(codeblock(traceback.format_exc(limit=7)))
            return
        finally:
            self.sessions.remove(task)
            if not late_task.done():
                late_task.cancel()

        with suppress(discord.HTTPException):
            await ctx.message.add_reaction(ctx.emoji('exec.ok'))

        result = task.result()

        if result is not None:
            self.last_result = result

        representation = repr(result)
        preamble = f'Executed in {timer}.'

        if isinstance(result, discord.File):
            try:
                await ctx.send(preamble, file=result)
            except discord.HTTPException as error:
                await ctx.send(f'Failed to automatically send `discord.File`: `{error}`')
            return

        if isinstance(result, discord.Embed):
            try:
                await ctx.send(preamble, embed=result)
            except discord.HTTPException as error:
                await ctx.send(f'Failed to automatically send `discord.Embed`: `{error}`')
            return

        if isinstance(result, str):
            representation = result
            preamble += ' (string)'

        message = f'{preamble}\n{codeblock(representation)}'

        if len(message) > 2000:
            file = discord.File(fp=StringIO(message), filename='result.txt')
            try:
                await ctx.send(file=file)
            except discord.HTTPException as error:
                await ctx.send(f'Cannot send result: `{error}`')
        else:
            await ctx.send(message)

    @group(name='eval', aliases=['exec', 'debug'], invoke_without_command=True)
    @is_owner()
    async def _eval(self, ctx, *, code: code_in_codeblock):  # type: ignore
        """Evaluates Python code in realtime."""
        await self.execute(ctx, code)

    @_eval.command(name='cancel')
    @is_owner()
    async def eval_cancel(self, ctx):
        """Cancels running code."""
        self.cancel_sessions()
        await ctx.ok()

    def cancel_sessions(self):
        """Cancel all running sessions."""
        for task in self.sessions:
            task.cancel()


def setup(bot):
    bot.add_cog(Exec(bot))
