import asyncio
from typing import Union

import discord
from discord.ext import menus

from .funcs import inflect_by_amount


def cool_button(func):
    async def wrapper(self, payload):
        if payload.event_type == 'REACTION_REMOVE':
            return
        r = await func(self, payload)
        await self.message.remove_reaction(str(payload.emoji), payload.member)
        return r
    return wrapper


class ResponseType:
    one_of_given    = 0
    every_of_given  = 1
    filter_of_given = 2

class Confirm(menus.Menu):
    def __init__(self, message: discord.Message, listen_to_ids: Union[list, set], response_type = ResponseType.one_of_given, timeout=60):
        super().__init__(message=message, timeout=timeout)
        self.message = message
        self.listen_to_ids = set(listen_to_ids)
        self.type = response_type

        if response_type == ResponseType.filter_of_given and timeout is None:
            raise TypeError('ты еблан')
        if response_type == ResponseType.one_of_given:
            self.result = None
        else: 
            self.result = set()


    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False
        if payload.user_id not in {self.bot.owner_id, *self.listen_to_ids, *self.bot.owner_ids}:
            return False
        return payload.emoji in self.buttons
    
    @menus.button('✅')
    async def do_confirm(self, payload: discord.RawReactionActionEvent):
        self.listen_to_ids.remove(payload.user_id)
        if self.type == ResponseType.one_of_given:
            self.result = True
            self.stop()
        else:
            self.result.add(payload.user_id)
            if len(self.listen_to_ids) == 0:
                if self.type == ResponseType.every_of_given:
                    self.result = True
                self.stop()

    
    @menus.button('❌')
    async def do_deny(self, payload):
        self.listen_to_ids.remove(payload.user_id)
        if self.type == ResponseType.filter_of_given:
            self.result.remove(payload.user_id)
            if len(self.listen_to_ids) == 0:
                self.stop()
        else:
            self.result = False
            self.stop()
    
    async def reconst(self, ctx):
        await self.start(ctx, wait=True)
        return self.result

class GateMenu(menus.Menu):
    def __init__(self, message, listen_to_ids):
        super().__init__(message=message, timeout=None)
        self.result = None
        self.listen_to_ids = listen_to_ids
    
    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False
        if payload.user_id not in {self.bot.owner_id, *self.listen_to_ids, *self.bot.owner_ids}:
            return False
        return payload.emoji in self.buttons
    
    @menus.button('⛩')
    async def pass_to_server(self, payload):
        self.result = True
        self.stop()
    @menus.button('⭕')
    async def kick_from_server(self, payload):
        self.result = False
        self.stop()
    
    async def reconst(self, ctx):
        await self.start(ctx, wait=True)
        return self.result



class SimpleListSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=10):
        super().__init__(entries, per_page=per_page)

    def format_page(self, menu: menus.MenuPages, page):
        if isinstance(page, discord.Embed):
            new_emb = page.copy()
            new_emb.set_footer(
                text     = (page.footer.text+" | " if page.footer.text else "") + self.page_numeration(menu), 
                icon_url = page.footer.icon_url
            )

            return new_emb
        else:
            return page
    
    def page_numeration(self, menu):
        page =  f'Страница {menu.current_page+1} из {self._max_pages}' if self.is_paginating else ""
        offset = self.per_page*menu.current_page
        if self.per_page > 1:
            upper = offset+self.per_page
            maximum = len(self.entries)
            element = f'Показано {offset+1}-{upper if upper < maximum else maximum} из {maximum}'
        else:
            element = False
        return f'{page or ""}{" | " if page and element else ""}{element or ""}'

class BasePages(menus.MenuPages):
    def __init__(self, source, include={'arrows', 'jump'}, *, timeout=600, **kwargs):
        super().__init__(source, timeout=timeout, **kwargs)
        self.input_lock = asyncio.Lock()

        if not 'standart' in include: 
            self.clear_buttons()
            if 'arrows' in include:
                self.add_button(menus.Button('◀', self.previous_page, position=menus.First(0)))
                self.add_button(menus.Button('▶', self.next_page, position=menus.Last(0)))
        if 'jump' in include:
            self.add_button(menus.Button('🔢', self.jump_page, position=menus.Last(1)))
        if timeout >= 600:
            self.add_button(menus.Button('⏹', self.makes_stop, position=menus.Last(2)))


    async def finalize(self, timed_out):
        try:
            if timed_out:
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except discord.HTTPException:
            pass

    async def start(self, ctx):
        self._ctx = ctx
        return await super().start(ctx, wait=True)

    @cool_button
    async def next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)
    @cool_button
    async def previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)
    @cool_button
    async def jump_page(self, payload):
        if self.input_lock.locked():
            return

        async with self.input_lock:
            channel = self.message.channel
            
            def check(m):
                return m.author.id == payload.member.id and \
                       m.channel == channel and \
                       m.content.isnumeric()

            to_delete = []
            to_delete.append(await self.message.channel.send('На какую страницу ты хочешь прыгнуть?'))

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=self.timeout)
            except asyncio.TimeoutError:
                to_delete.append(await channel.send('Слишком долгий ответ'))
                await asyncio.sleep(5)
            else:
                page = int(msg.content)
                to_delete.append(msg)
                await self.show_checked_page(page - 1)
            
            try:
                await channel.delete_messages(to_delete)
            except: pass
    @cool_button
    async def makes_stop(self, payload):
        self.stop()

class LyashaPages(BasePages):
    def __init__(self, entries, **kwargs):
        source = SimpleListSource(entries, **kwargs)
        super().__init__(source, **kwargs)


class ScoringListSource(SimpleListSource):
    def format_page(self, menu, page):
        offset = self.per_page*menu.current_page
        return discord.Embed(
            title = '🏮 Топ по очкам',
            color = 0xcc0f1f,
            description ='\n'.join([f'{i+1}. <@{model.discord_id}> — {inflect_by_amount(model.score, "очко")}' for i, model in enumerate(page, start=offset)]) 
        ).set_footer(
            text = self.page_numeration(menu)
        )

class ScoringPages(BasePages):
    def __init__(self, entries, **kwargs):
        source = ScoringListSource(entries, **kwargs)
        super().__init__(source, **kwargs)