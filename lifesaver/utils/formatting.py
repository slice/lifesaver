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
