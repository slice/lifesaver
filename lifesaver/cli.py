# encoding: utf-8

import asyncio
import importlib

import click
import ruamel.yaml
from lifesaver.bot import Bot, BotConfig
from lifesaver.config import ConfigError
from lifesaver.logging import setup_logging


def resolve_class(specifier: str):
    module, class_name = specifier.split(":")
    imported = importlib.import_module(module)
    loaded_class = getattr(imported, class_name)
    return loaded_class


async def _postgres_connect(bot):
    try:
        import asyncpg
    except ImportError:
        raise RuntimeError("Cannot connect to Postgres, asyncpg is not installed")

    bot.log.debug("creating a postgres pool")
    bot.pool = await asyncpg.create_pool(dsn=bot.config.postgres["dsn"])
    bot.log.debug("created postgres pool")


@click.command()
@click.option("--config", default="config.yml", help="The configuration file to use.")
@click.option(
    "--no-default-cogs",
    is_flag=True,
    default=False,
    help="Prevent default cogs from loading.",
)
def cli(config, no_default_cogs):
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    loop = asyncio.get_event_loop()

    try:
        # Manually load the config first in order to detect a custom config
        # class to use.
        #
        # We must do this because the custom config class is specified in the
        # config itself, and we don't know which config class to load yet.
        with open(config, "r") as fp:
            first_config = ruamel.yaml.YAML().load(fp)

        config_class = BotConfig

        custom_config_class = first_config.get("config_class")
        if custom_config_class:
            config_class = resolve_class(custom_config_class)

        config = config_class.load(config)
    except ruamel.yaml.error.YAMLError as error:
        raise ConfigError("Invalid config. Is the syntax correct?") from error
    except FileNotFoundError as error:
        raise ConfigError(f"No config file was found at {config}.") from error

    bot_class = Bot

    if config.bot_class:
        bot_class = resolve_class(config.bot_class)

        if not issubclass(bot_class, Bot):
            raise TypeError("Custom bot class is not a subclass of lifesaver.bot.Bot")

    with setup_logging(config.logging):
        bot = bot_class(config)

        if bot.config.postgres and bot.pool is None:
            loop.run_until_complete(_postgres_connect(bot))

        bot.load_all(exclude_default=no_default_cogs)
        bot.run()


if __name__ == "__main__":
    cli()
