from pathlib import Path

from discord.ext import commands


class Bot(commands.Bot):
    """
    A ``commands.Bot`` subclass that provides useful utilities.
    """
    def __init__(self, *args, extensions_path, **kwargs):
        super().__init__(*args, **kwargs)

        #: The path from which to load extensions from, relative to the current directory.
        self.extensions_path = extensions_path

        #: A list of extensions names to reload when calling Bot.load_all().
        self._extension_load_list = []

    def _rebuild_load_list(self):
        """Rebuilds the load list."""

        # Transforms a path like ``exts/hi.py`` to ``exts.hi``.
        def transform_path(path):
            return str(path).replace('/', '.').replace('.py', '')

        # Build a list of extensions to load.
        exts_path = Path(self.extensions_path)
        paths = [transform_path(x) for x in exts_path.glob('**/*.py') if x.name != '__init__.py']

        self._extension_load_list = paths + ['lifesaver.bot.exts.admin']

    def load_all(self, *, unload_first=False):
        """
        Loads all extensions in the extensions path.

        :param unload_first: Specifies whether to unload an extension before loading it.
        """
        self._rebuild_load_list()

        for extension_name in self._extension_load_list:
            if unload_first:
                self.unload_extension(extension_name)
            self.load_extension(extension_name)

        self.dispatch('lf_bot_load_all', unload_first)
