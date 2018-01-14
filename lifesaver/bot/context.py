import discord
from discord.ext import commands


class Context(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._paginator = commands.Paginator()

    def __iadd__(self, line: str) -> 'Context':
        self._paginator.add_line(line)
        return self

    async def send_pages(self, *, prefix: str = '```', suffix: str = '```'):
        self._paginator.prefix = prefix
        self._paginator.suffix = suffix
        for page in self._paginator.pages:
            await self.send(page)

    async def ok(self, emoji='\N{OK HAND SIGN}'):
        """Makes the bot respond with an emoji in acknowledgement to an action performed by the user."""
        actions = [self.message.add_reaction, self.send, self.author.send]

        for action in actions:
            try:
                await action(emoji)
                break
            except discord.HTTPException:
                pass
