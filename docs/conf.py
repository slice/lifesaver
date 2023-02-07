# encoding: utf-8
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "lifesaver"
copyright = "2018, slice"
author = "slice"

# The short X.Y version
version = "0.0.0"

# The full version, including alpha/beta/rc tags
release = "0.0.0"

html_experimental_html5_builder = True

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.napoleon",
    "sphinxcontrib.asyncio",
]

rst_prolog = """
.. |coro| replace:: This function is a |corourl|_.
.. |corourl| replace:: *coroutine*
.. _corourl: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "discord.py": ("https://discordpy.readthedocs.io/en/latest/", None),
    "aiohttp": ("https://aiohttp.readthedocs.io/en/stable/", None),
    "jishaku": ("https://jishaku.readthedocs.io/en/latest/", None),
}

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
html_theme = "basic"
html_static_path = ["_static"]
