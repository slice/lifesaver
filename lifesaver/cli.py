import asyncio
import importlib
import logging

import click
from lifesaver.bot import Bot, BotConfig
from lifesaver.logging import setup_logging


@click.command()
@click.option('--config', default='config.yml', help='The configuration file to use.')
def cli(config):
    setup_logging()
    log = logging.getLogger('lifesaver.cli')

    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        log.info('Using uvloop')
    except ImportError:
        log.warn('uvloop not found, not using')

    config = BotConfig.load(config)
    custom_bot_module = getattr(config, 'bot_class')
    bot_class = Bot

    if custom_bot_module is not None:
        module, class_name = custom_bot_module.split(':')
        imported = importlib.import_module(module)
        bot_class = getattr(imported, class_name)

        if not issubclass(bot_class, Bot):
            raise TypeError('Custom bot class is not a subclass of lifesaver.bot.Bot')

        log.debug('Using custom bot class: %s', bot_class)

    log.info('Booting bot.')
    bot = bot_class.with_config_instance(config)
    bot.load_all()
    bot.run()


if __name__ == '__main__':
    cli()
