import os
import sys
import traceback

import discord
from discord.ext import commands


initial_extensions = (
    'cogs.admin',
    'cogs.help',
    'cogs.logs',
    'cogs.roles',
    'cogs.scoring',
    'cogs.status',
    'cogs.triggers',
    'cogs.welcome',

    'games.rockpaperscissors',
    'games.tictactoe',
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

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file = sys.stderr)
                traceback.print_exc()
    
    async def on_ready(self):
        print('Бот загружен')
        print(self.user)
        if os.environ['IS_HEROKU'] == '1':
            await self.get_channel(827504142406385664).send(
                embed = discord.Embed(
                    description = 'Бот загружен', 
                    timestamp = self._program_start
                ).set_footer(
                    text = self.command_prefix
                )
            )