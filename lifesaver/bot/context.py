import discord
from discord.ext.commands import Context


class LifesaverContext(Context):
    async def ok(self, emoji='\N{OK HAND SIGN}'):
        """
        Makes the bot respond with an emoji in acknowledgement to a action.
        """
        actions = [
            self.message.add_reaction,
            self.send,
            self.author.send
        ]

        for action in actions:
            try:
                await action(emoji)
                break
            except discord.HTTPException:
                pass
