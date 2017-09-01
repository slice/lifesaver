from lifesaver.bot import Bot
from lifesaver.logging import setup_logging


class SampleBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_all()


if __name__ == '__main__':
    setup_logging()
    SampleBot.with_config().run()
