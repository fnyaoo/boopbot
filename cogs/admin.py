import discord
from discord.ext import commands

from checks import is_admin
from utils import MembersDB as modaler


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._qualified_name = 'Админ-команды'
        self.description = 'Солянка команд Егора для всяких приколов'

    @commands.command(name='purge')
    @is_admin()
    async def _purge(self, ctx, amount: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)

    @commands.command(name='getdata')
    @is_admin()
    async def show_json(self, ctx, target: discord.Member = None):
        target = target or ctx.author
        member = modaler(target.id).member
        await ctx.reply(f'```py\n{member.json}```')
    
def setup(bot):
    bot.add_cog(AdminCommands(bot))