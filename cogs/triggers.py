import re

import discord
from discord.ext import commands
from discord.utils import find

from utils import layout


class Triggers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.regex = re.compile(r"<;(?P<name>[a-zA-Z0-9_]{2,32});>", flags = re.DOTALL)
        print(self.regex)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        if message.author.bot:
            return

        content = message.content
        
        if len(re.findall(self.regex, content)) > 0:
            def subfunc(matchobj: re.Match):
                print(f"Match was found at {matchobj.start()}-{matchobj.end()}: {matchobj.group('name')}")
                emoji = find(lambda x: x.name == matchobj.group('name'), self.bot.emojis)
                if not emoji is None: return str(emoji)
                else: return matchobj.group('name')

            content = re.sub(self.regex, subfunc, content)
            return await self.send_webhooked(message, content, 'Анимированный эмоджи')

        if 'TADA' in content:
            await message.add_reaction('🎉')
        if 'LD' in content:
            await message.add_reaction('👍')
            await message.add_reaction('👎')
        if '<3' in content:
            await message.add_reaction('♥')
    
    async def send_webhooked(self, message, content, reason=None):
        wh = await message.channel.create_webhook(
            name = message.author.display_name, 
            avatar = await message.author.avatar.read(),
            reason = reason
        )
        await message.delete()
        await wh.send(content)
        await wh.delete()
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction.emoji) != '🔁':
            return
        msg = reaction.message
        if msg.author != user:
            return

        await self.send_webhooked(msg, f'{msg.content.translate(layout)}\n> **Исправлена раскладка клавиатуры**', 'Исправление раскладки')


def setup(bot):
    bot.add_cog(Triggers(bot))
