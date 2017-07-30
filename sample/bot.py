import logging
import os
from lifesaver.bot import Bot

logging.basicConfig(level=logging.INFO)

bot = Bot('^', extensions_path='sample/exts')
bot.load_all()
bot.run(os.environ['TOKEN'])
