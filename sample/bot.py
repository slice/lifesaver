import logging
import os

from lifesaver.bot import Bot
from lifesaver.logging import setup_logging

setup_logging()

bot = Bot('^', extensions_path='sample/exts')
bot.load_all()
bot.run(os.environ['TOKEN'])
