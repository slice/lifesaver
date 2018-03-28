# -*- coding: utf-8 -*-
"""

Some code taken from: https://github.com/b1naryth1ef/b1nb0t/

=================================================================================

MIT License

Copyright (c) 2017 - 2018 slice
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

import io
import logging
import textwrap
import traceback
from contextlib import redirect_stdout, suppress
from typing import Dict, Any, List, TypeVar, Callable, Union

import discord
from discord.ext import commands

from lifesaver.bot import Cog, Context, command
from lifesaver.utils import codeblock

log = logging.getLogger(__name__)

IMPLICIT_RETURN_STOP_WORDS = {
    'continue', 'break', 'raise', 'yield', 'with', 'assert', 'del', 'import', 'pass', 'return', 'from'
}


class Code(commands.Converter):
    def __init__(self, *, wrap_code: bool = False, strip_ticks: bool = True, indent_width: int = 4,
                 implicit_return: bool = False):
        """
        Transforms code in certain ways.

        Parameters
        ----------
        wrap_code : bool
            Specifies whether to wrap the resulting code in a function.
        strip_ticks : bool
            Specifies whether to strip the code of Markdown-related backticks.
        indent_width : int
            Specifies the indent width, if wrapping.
        implicit_return : bool
            Automatically adds a return statement, if wrapping.
        """
        self.wrap_code = wrap_code
        self.strip_ticks = strip_ticks
        self.indent_width = indent_width
        self.implicit_return = implicit_return

    async def convert(self, ctx: Context, arg: str) -> str:
        result = arg

        if self.strip_ticks:
            # remove codeblock ticks
            if result.startswith('```') and result.endswith('```'):
                result = '\n'.join(result.split('\n')[1:-1])

            # remove inline code ticks
            result = result.strip('` \n')

        if self.wrap_code:
            # wrap in a coroutine and indent
            result = 'async def func():\n' + textwrap.indent(result, ' ' * self.indent_width)

        if self.wrap_code and self.implicit_return:
            last_line = result.splitlines()[-1]

            # if the last line isn't indented and not returning, add it
            first_word = last_line.strip().split(' ')[0]
            no_stop = all(first_word != word for word in IMPLICIT_RETURN_STOP_WORDS)
            if not last_line[4:].startswith(' ') and no_stop:
                last_line = (' ' * self.indent_width) + 'return ' + last_line[4:]

            result = '\n'.join(result.splitlines()[:-1] + [last_line])

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
            # id, name#discrim, display name, name
            return member.id == specifier or str(member) == specifier or member.display_name == specifier \
                   or member.name == specifier

        return discord.utils.find(_finder, ctx.guild.members)

    T = TypeVar('T')

    def grabber(lst: List[T]) -> Callable[[int], T]:
        """Returns a function that, when called, grabs an item by ID from a list of objects with an ID."""

        def _grabber_function(thing_id: int) -> T:
            return discord.utils.get(lst, id=thing_id)

        return _grabber_function

    env = {
        'bot': ctx.bot,
        'ctx': ctx,
        'msg': ctx.message,
        'guild': ctx.guild,
        'channel': ctx.channel,
        'me': ctx.message.author,
        'cog': cog,

        # modules
        'discord': discord,
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

        self.last_result = None

    async def execute(self, ctx: Context, code: str):
        log.info('Eval: %s', code)

        env = create_environment(self, ctx)

        # define the wrapped function
        try:
            exec(compile(code, '<exec>', 'exec'), env)
        except SyntaxError as e:
            # send pretty syntax errors
            await ctx.send(format_syntax_error(e))
            return

        # grab the defined function
        func = env['func']

        try:
            # execute the code
            ret = await func()
        except Exception:
            # something went wrong :(
            with suppress(discord.HTTPException):
                await ctx.message.add_reaction('\N{EXCLAMATION QUESTION MARK}')

            # send stream and what we have
            await ctx.send(codeblock(traceback.format_exc(limit=7), lang='py'))
            return

        with suppress(discord.HTTPException):
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

        # set the last result, but only if it's not none
        if ret is not None:
            self.last_result = ret

        message = codeblock(repr(ret), lang='py')

        if len(message) > 2000:
            # too long
            await ctx.send('Result was too long.')
        else:
            # message was under 2k chars, just send!
            await ctx.send(message)

    @command(name='eval', aliases=['exec', 'debug'])
    @commands.is_owner()
    async def _eval(self, ctx, *, code: Code(wrap_code=True, implicit_return=True)):
        """Executes Python code."""
        await self.execute(ctx, code)


def setup(bot):
    bot.add_cog(Exec(bot))
