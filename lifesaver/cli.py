# encoding: utf-8

import asyncio
import importlib

import click
from lifesaver.bot import Bot, BotConfig
from lifesaver.config import ConfigError
from lifesaver.logging import setup_logging


@click.command()
@click.option('--config', default='config.yml', help='The configuration file to use.')
@click.option('--no-default-cogs', is_flag=True, default=False, help='Prevent default cogs from loading.')
def cli(config, no_default_cogs):
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    try:
        config = BotConfig.load(config)
    except FileNotFoundError as error:
        raise ConfigError(f'No config file was found at {config}.') from error

    custom_bot_module = getattr(config, 'bot_class', None)
    bot_class = Bot

    if custom_bot_module is not None:
        module, class_name = custom_bot_module.split(':')
        imported = importlib.import_module(module)
        bot_class = getattr(imported, class_name)

        if not issubclass(bot_class, Bot):
            raise TypeError('Custom bot class is not a subclass of lifesaver.bot.Bot')

    with setup_logging():
        bot = bot_class(config)
        bot.load_all(exclude_default=no_default_cogs)
        bot.run()


if __name__ == '__main__':
    cli()
