# encoding: utf-8

from typing import Callable, Any, Type, Union, List, Set

import discord


async def history_reducer(ctx, reducer: Callable[[discord.Message], Any], *, ignore_duplicates=False,
                          result_container_type: Type = list, **kwargs) -> Union[List, Set]:
    """Iterate through message history and output a list of items determined by a function that receives each message.

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
    if 'limit' not in kwargs:
        raise TypeError('limit required')

    history: List[discord.Message] = await ctx.history(limit=kwargs['limit']).flatten()
    results: Union[List, Set] = result_container_type()

    for message in history:
        result = await discord.utils.maybe_coroutine(reducer, message)

        if result:
            if ignore_duplicates and result in results:
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
                    results.add(results)

    return results
