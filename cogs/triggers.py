import re

import discord
from discord.ext import commands

from utils import layout


class Triggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.regex = re.compile('<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        content = message.content
        
        if not message.author.premium_since:
            if re.match(self.regex, content):
                return await self.send_webhook(message, content, 'Анимированный бейдж')

        if 'TADA' in content:
            await message.add_reaction('🎉')
        if 'LD' in content:
            await message.add_reaction('👍')
            await message.add_reaction('👎')
        if '<3' in content:
            await message.add_reaction('♥')
    
    async def send_webhook(self, message, content, reason=None):
        wh = await message.channel.create_webhook(
            name = message.author.display_name, 
            avatar = await message.author.avatar.read(),
            reason = reason
        )
        await message.delete(reason = reason)
        await wh.send(content)
        await wh.delete(reason = reason)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction.emoji) != '🔁':
            return
        msg = reaction.message
        if msg.author != user:
            return

        await self.send_webhook(msg, f'{msg.content.translate(layout)}\n> **Исправлена раскладка клавиатуры**', 'Исправление раскладки')


def setup(bot):
    bot.add_cog(Triggers(bot))
