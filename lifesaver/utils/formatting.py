def codeblock(code: str, *, lang: str = '') -> str:
    """
    Constructs a Markdown codeblock.

    :param code: The code.
    :type code: str
    :param lang: The language.
    :type lang: str
    :return: The formatted codeblock.
    :rtype: str
    """
    return "```{}\n{}\n```".format(lang, code)


def truncate(text: str, desired_length: int) -> str:
    """
    Truncates text.

    :param text: The text to truncate.
    :type text: str
    :param desired_length: The desired length.
    :type desired_length: int
    :return: The truncated text.
    :rtype: str
    """
    if len(text) > desired_length:
        return text[:desired_length-3] + '...'
    else:
        return text
