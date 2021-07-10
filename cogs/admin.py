import discord
from discord.ext import commands
from typing import Dict, List

from checks import is_admin
from utils.database import MembersDB as modaler


class AdminFlags(commands.FlagConverter, prefix='--', delimiter=' '):
    target: List[discord.Member] = commands.flag(aliases=['member'], default=[])
    limit: int = commands.flag(aliases=['count'], default=10)

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self._qualified_name = 'Админ-команды'
        self.description = 'Солянка команд Егора для всяких приколов'

    @commands.command(name='purge')
    @is_admin()
    async def _purge(self, ctx: commands.Context, *, flags: AdminFlags):
        def is_target(m):
            return m.author in flags.target if len(flags.target) > 0 else True
        
        await ctx.message.delete()
        deleted: List[discord.Message] = await ctx.channel.purge(limit=flags.limit, check=is_target)
        
        text: Dict[discord.Member, int] = {}
        for message in deleted:
            i = text.get(message.author, 0)
            text[message.author] = i + 1

        await ctx.send(
            embed=discord.Embed(
                title = f'✅ Удалено {len(deleted)} сообщений',
                color = 0x77b255,
                description = '\n'.join([f'{author.mention}: {count} сообщений' for author, count in text.items()])
            )
        )

    @commands.command(name='getdata')
    @is_admin()
    async def show_json(self, ctx, *, flags: AdminFlags):
        targets = flags.target
        await ctx.reply('\n'.join([f'```py\n{modaler(target.id).member.json}\n```' for target in targets]))
    
def setup(bot):
    bot.add_cog(AdminCommands(bot))