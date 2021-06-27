import discord
from discord.ext import commands

from utils import layout


class Triggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        content = message.content
        if 'TADA' in content:
            await message.add_reaction('🎉')
        if 'LD' in content:
            await message.add_reaction('👍')
            await message.add_reaction('👎')
        if '<3' in content:
            await message.add_reaction('♥')
    
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction.emoji) != '🔁':
            return
        msg = reaction.message
        if msg.author != user:
            return

        rsn = 'Исправление раскладки'
        wh = await msg.channel.create_webhook(
            name = user.display_name, 
            avatar = await user.avatar.url.read(),
            reason = rsn
        )

        await msg.delete()
        await wh.send(f'{msg.content.translate(layout)}\n> **Исправлена раскладка клавиатуры**')
        await wh.delete()


def setup(bot):
    bot.add_cog(Triggers(bot))
