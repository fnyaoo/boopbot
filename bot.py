import os
import sys
import traceback
from datetime import datetime

import discord
from discord.ext import commands
from dislash import SlashClient


initial_extensions = (
    'cogs.admin',
    'cogs.fun',
    'cogs.help',
    'cogs.logs',
    'cogs.roles',
    'cogs.scoring',
    'cogs.stars',
    'cogs.status',
    'cogs.triggers',
    'cogs.welcome',

    'games.rockpaperscissors',
    'games.tictactoe',

    'jishaku',
    'events'
)

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    return [f'<@!{user_id}> ', f'<@{user_id}> ', '!']

class BoopBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = _prefix_callable,
            strip_after_prefix = True,
            intents = discord.Intents.all()
        )
        self._program_start = discord.utils.utcnow()
        SlashClient(self, modify_send = False)

        loaded = []
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Ошибка при загрузке {extension}.', file = sys.stderr)
                traceback.print_exc()
            else:
                loaded.append(extension)
        print('Загружено: ' + ', '.join(loaded))
    
    async def on_ready(self):
        print('Бот загружен')
        print(self.user)
        if os.environ['IS_HEROKU'] == '1':
            await self.get_channel(827504142406385664).send(
                embed = discord.Embed(
                    description = f'Бот запущен\nВремя запуска: {discord.utils.format_dt(self._program_start, "R")}'
                ).set_footer(
                    text = 'Префикс: !'
                )
            )
    
    async def get_or_fetch_member(self, guild: discord.Guild, member_id):
        member = guild.get_member(member_id)
        if member is None:
            member = await guild.fetch_member(member_id)
        return member