import random
from typing import Dict, List, Tuple

import discord
from discord.ext import commands
from discord.ext.commands.core import command

from utils.funcs import inflect_by_amount
from checks import is_admin


class AdminFlags(commands.FlagConverter, prefix = '/', delimiter = ' '):
    target: Tuple[discord.Member, ...] = commands.flag(aliases = ['t', 'member', 'members', 'targets', 'from', 'от'], default = [])
    limit: int                         = commands.flag(aliases = ['l', 'amount', 'кол-во', 'лимит'], default = 50)
    contains: str                      = commands.flag(aliases = ['c', 'содержит'], default = None)
    before: discord.Message            = commands.flag(aliases = ['b', 'до'], default = None)
    after: discord.Message             = commands.flag(aliases = ['a', 'после'], default = None)
    expression: str                    = commands.flag(aliases = ['e', 'operator', 'оператор'], default = 'and')

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self._qualified_name = 'Админ-команды'
        self.description = 'Солянка команд Егора для всяких приколов'

    @commands.command(name = 'purge')
    @is_admin()
    async def _purge(self, ctx: commands.Context, *, flags: AdminFlags):
        ch: discord.TextChannel = ctx.channel
        def is_target(m):
            if m == ctx.message:
                return False
            condition = [True]
            if len(flags.target) > 0:
                condition.append(m.author in flags.target)
            if flags.contains is not None:
                condition.append(flags.contains.casefold() in m.content.casefold())
            
            exp = flags.expression
            if exp in ('and', 'и', 'all', 'все'):
                method = all
            elif exp in ('or', 'или', 'any', 'любое'):
                method = any
            elif exp in ('xor', 'отрицательное или'):
                def method(c):
                    return (not all(c)) or any(c)
            else:
                raise commands.BadArgument(f'Неизвестный оператор {exp}')
            return method(condition)

        kwargs = {
            'limit': flags.limit+1,
            'check': is_target,
            'before': flags.before,
            'after': flags.after
        }

        deleted: List[discord.Message] = await ch.purge(**kwargs)

        text: Dict[discord.Member, int] = {}
        for message in deleted:
            i = text.get(message.author, 0)
            text[message.author] = i + 1

        await ctx.send(
            embed = discord.Embed(
                title = f'✅ Удалено {inflect_by_amount(len(deleted), "сообщений")} из {flags.limit} последних',
                color = 0x77b255,
                description = '\n'.join([f'{author.mention}: {inflect_by_amount(count, "сообщений")}' for author, count in text.items()])
            )
        )
    
def setup(bot):
    bot.add_cog(AdminCommands(bot))