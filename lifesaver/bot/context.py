import discord
from discord.ext.commands import Context


class LifesaverContext(Context):
    async def ok(self, emoji='\N{OK HAND SIGN}'):
        """
        Makes the bot respond with an emoji in acknowledgement to a action.
        """
        actions = [
            self.message.add_reaction(emoji),
            self.send(emoji),
            self.author.send(emoji)
        ]

        for action in actions:
            try:
                await action
                break
            except discord.HTTPException:
                pass
