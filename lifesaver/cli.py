import asyncio
import logging

import click
from lifesaver.bot import Bot
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

    bot = Bot.with_config(config)
    bot.load_all()
    bot.run()


if __name__ == '__main__':
    cli()
