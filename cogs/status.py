from datetime import datetime as dt

import discord
from discord.ext import commands, tasks


class StatusBar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.message = self.bot.get_channel(832275479729930311).get_partial_message(846793823359205396)
        self.ticker.start()


    async def fetch(self):
        guild = self.message.guild

        vc_member_count = 0
        for vc_channel in guild.voice_channels:
            vc_member_count + =  len(vc_channel.members)

        embed = discord.Embed(
            title = guild.name,
            color = 0x6947B3,
            timestamp = dt.utcnow(),
            description = f'Количество участников: `{guild.member_count}`\n' \
                # f'В чате сейчас {inflect_by_amount(len(self.bot.cogs["ScoringSystem"].handled), "человек")}\n' \
                f'В войсей сейчас: {vc_member_count}\n'
        ).set_image(
            url = guild.icon.url
        )
        await self.message.edit(embed = embed)

    @tasks.loop(minutes = 1)
    async def ticker(self):
        await self.fetch()

def setup(bot):
    bot.add_cog(StatusBar(bot))