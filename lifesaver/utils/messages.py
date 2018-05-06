# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2017 - 2018 slice

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
from typing import Callable, Any, Type, Union, List, Set

import discord


async def history_reducer(ctx, reducer: Callable[[discord.Message], Any], *, ignore_duplicates=False,
                          result_container_type: Type = list, **kwargs) -> Union[List, Set]:
    """
    Iterates through message history, and outputs a list of items determined by a function that receives each
    message.

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
