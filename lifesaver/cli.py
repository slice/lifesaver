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

        config_instance: BotConfig = config_class.load(config)
    except ruamel.yaml.error.YAMLError as error:  # type: ignore
        raise ConfigError("Invalid config. Is the syntax correct?") from error
    except FileNotFoundError as error:
        raise ConfigError(f"No config file was found at {config}.") from error

    bot_class = Bot

    if config_instance.bot_class:
        bot_class = resolve_class(config_instance.bot_class)

        if not issubclass(bot_class, Bot):
            raise TypeError("Custom bot class is not a subclass of lifesaver.bot.Bot")

    with setup_logging(config_instance.logging):
        bot = bot_class(config_instance)

        async def main():
            async with bot:
                await bot.load_all(exclude_default=no_default_cogs)
                await bot.start(bot.config.token)

        asyncio.run(main())


if __name__ == "__main__":
    cli()
