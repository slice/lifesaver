def codeblock(code, *, lang=''):
    """
    Constructs a Markdown codeblock.

    :param code: The code.
    :param lang: The language.
    :return: The formatted codeblock.
    """
    return "```{}\n{}\n```".format(lang, code)
