"""
MIT License

Copyright (c) 2017 - 2018 slice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
from typing import Optional, Any, List
from math import ceil

import discord

__all__ = ['Paginator', 'ListPaginator']
log = logging.getLogger(__name__)


class Paginator:
    def __init__(
        self,
        invoker: discord.User,
        destination: discord.abc.Messageable,
        *, bot
    ) -> None:
        self.invoker = invoker
        self.bot = bot
        self.destination = destination
        self.message: Optional[discord.Message] = None
        self.page = 0
        self.stopped = False

    @property
    def actions(self):
        return {
            "\N{BLACK SQUARE FOR STOP}": self.stop,
            "\N{BLACK LEFT-POINTING TRIANGLE}": self.previous,
            "\N{BLACK RIGHT-POINTING TRIANGLE}": self.next,
        }

    def get_page_contents(self, page: int) -> str:
        raise NotImplementedError()

    @property
    def max_pages(self):
        return NotImplemented

    async def stop(self):
        await self.message.delete()
        self.stopped = True

    async def previous(self):
        if self.page == 0:
            return
        self.page -= 1
        await self.update()

    async def next(self):
        if self.page == self.max_pages - 1:
            return
        self.page += 1
        await self.update()

    def reaction_check(self, reaction: discord.Reaction, user: discord.User) -> bool:
        conditions = [
            not user.bot,
            reaction.emoji in self.actions.keys(),
            reaction.message.id == self.message.id,
            user == self.invoker,
        ]

        log.debug('Checks: %s', conditions)

        return all(conditions)

    def get_base_embed(self) -> discord.Embed:
        return discord.Embed()

    def get_embed_for_page(self, page: int) -> discord.Embed:
        embed = self.get_base_embed()
        embed.description = self.get_page_contents(page)
        embed.set_footer(text=f'Page {page + 1}/{self.max_pages}')
        return embed

    async def handle_reaction(self, reaction: discord.Reaction, user: discord.User):
        emoji = reaction.emoji

        action = self.actions.get(emoji)
        log.debug('Grabbed action for %s: %s', emoji, action)

        if action:
            await discord.utils.maybe_coroutine(action)

    async def handle_events(self):
        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=self.reaction_check)
            await self.handle_reaction(reaction, user)

            if self.stopped:
                log.debug('Paginator stopped, breaking.')
                break

            try:
                await self.message.remove_reaction(reaction.emoji, user)
            except discord.HTTPException:
                pass

    async def update(self):
        if self.stopped:
            return

        embed = self.get_embed_for_page(self.page)

        try:
            await self.message.edit(embed=embed)
        except discord.NotFound:
            # hmm, message does't exist. let's stop.
            self.stopped = True

    async def create(self):
        embed = self.get_embed_for_page(0)
        self.message = await self.destination.send(embed=embed)

        for emoji in self.actions.keys():
            await self.message.add_reaction(emoji)

        await self.handle_events()


class ListPaginator(Paginator):
    def __init__(
        self,
        things: List[Any],
        *args,
        title: str = None,
        per_page: int = 10,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = title
        self.things = things
        self.per_page = per_page

    def get_base_embed(self) -> discord.Embed:
        if self.title:
            return discord.Embed(title=self.title)
        else:
            return super().get_base_embed()

    @property
    def max_pages(self):
        return ceil(len(self.things) / self.per_page)

    def format_things(self, things: List[Any]) -> str:
        return '\n'.join(map(lambda thing: f'\N{BULLET} {thing}', things))

    def get_page_contents(self, page: int) -> str:
        starting_index = page * self.per_page
        things = self.things[starting_index:starting_index + self.per_page]
        return self.format_things(things)
