import os

from lifesaver.bot import Bot
from lifesaver.logging import setup_logging


class SampleBot(Bot):
    def __init__(self):
        super().__init__(os.environ.get('PREFIX', '/'), extensions_path='sample/exts')
        self.load_all()


if __name__ == '__main__':
    setup_logging()
    bot = SampleBot()
    bot.run(os.environ['TOKEN'])
