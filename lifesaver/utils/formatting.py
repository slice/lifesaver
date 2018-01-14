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


def codeblock(code: str, *, lang: str = '') -> str:
    """
    Constructs a Markdown codeblock.

    Parameters
    ----------
    code : str
        The code to insert into the codeblock.
    lang : str, optional
        The string to mark as the language when formatting.

    Returns
    -------
    str
        The formatted codeblock.
    """
    return "```{}\n{}\n```".format(lang, code)


def truncate(text: str, desired_length: int, *, suffix: str = '...') -> str:
    """
    Truncates text. Three periods will be inserted as a suffix by default, but this can be changed.

    Parameters
    ----------
    text : str
        The text to truncate.
    desired_length : int
        The desired length.
    suffix : str, optional
        The text to insert before the desired length is reached. By default, this is "..." to indicate truncation.
    """
    if len(text) > desired_length:
        return text[:desired_length - len(suffix)] + suffix
    else:
        return text
