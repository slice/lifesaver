# encoding: utf-8

__all__ = ['mentionable_role']

import contextlib

import discord


@contextlib.asynccontextmanager
async def mentionable_role(role: discord.Role):
    """An asynchronous context manager that edits a role to be mentionable,
    yields, then edits the role to be unmentionable.

    Keep in mind that this can raise if you don't have the proper permissions to
    edit the role.

    In case your code raises, the role will be edited to be unmentionable (using
    a ``finally`` clause).

    Example
    -------

    .. code:: python3

        # Assuming that you have the proper permissions:

        async with mentionable_role(role):
            # `role` should be mentionable here.
            await channel.send(f'{role.mention} yo!')

        # `role` is no longer mentionable.
    """
    if not role.mentionable:
        await role.edit(mentionable=True)

    try:
        yield
    finally:
        await role.edit(mentionable=False)
