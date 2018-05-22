# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2017 - 2018 slice, FrostLuma

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


class SubcommandInvocationRequired(commands.CommandError):
    """A :class:`CommandError` subclass raised when a subcommand needs to be invoked."""
    pass


class Command(commands.Command):
    """A :class:`commands.Command` subclass that implements additional useful features."""

    def __init__(self, *args, typing: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        #: Specifies whether to send typing indicators while the command is running.
        self.typing = typing

    async def invoke(self, ctx):
        if self.typing:
            async with ctx.typing():
                await super().invoke(ctx)
        else:
            await super().invoke(ctx)


class GroupMixin(commands.GroupMixin):
    def command(self, *args, **kwargs):
        def decorator(func):
            cmd = command(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        def decorator(func):
            cmd = group(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator


class Group(GroupMixin, commands.Group, Command):
    def __init__(self, *args, hollow: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        #: Specifies whether a subcommand must be invoked.
        self.hollow = hollow

    async def invoke(self, ctx):
        if ctx.view.eof and self.hollow:
            # complain if we're at the end and we still need a subcommand
            raise SubcommandInvocationRequired()
        await super().invoke(ctx)


def group(*args, **kwargs):
    return command(*args, cls=Group, **kwargs)


def command(name: str = None, cls=Command, **kwargs):
    return commands.command(name, cls, **kwargs)
