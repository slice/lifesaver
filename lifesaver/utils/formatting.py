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
