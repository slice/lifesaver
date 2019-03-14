# encoding: utf-8

from typing import Callable, Any, Type, Union, List, Set

import discord


async def history_reducer(
    ctx,
    reducer: Callable[[discord.Message], Any],
    *,
    ignore_duplicates: bool = False,
    result_container_type: Type = list,
    **kwargs,
) -> Union[List, Set]:
    """Iterate through message history and output a list of items built from
    a function that receives each message.

    Parameters
    ----------
    ctx : lifesaver.bot.Context
        The command context.
    reducer
        The callable reducer. Results that aren't falsy are added to the result container.
    ignore_duplicates
        Specifies whether duplicates should be ignored.
    result_container_type
        Specifies the type of result container. Should be either ``list`` or ``set``.
    kwargs
        The kwargs to pass to the ``ctx.history`` method.

    Returns
    -------
        The list of items.
    """
    results: Union[List, Set] = result_container_type()

    async for message in ctx.history(**kwargs):
        result = await discord.utils.maybe_coroutine(reducer, message)

        if not result or (ignore_duplicates and result in results):
            continue

        if isinstance(results, list):
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
        elif isinstance(results, set):
            if isinstance(result, set):
                results = results | result
            else:
                results.add(result)

    return results
