import os

os.environ['IS_HEROKU'] = "1" if 'HEROKU_APP_ID' in os.environ else "0"


from datetime import datetime
import discord
from discord.ext import commands

from utils import config

program_start = datetime.utcnow()
bot = commands.Bot(
    # '?',
    config['prefix'],
    intents = discord.Intents.all()
)


bot.load_extension('events')
bot.load_extension('cogs')
bot.load_extension('games')
bot.load_extension('jishaku')


@bot.event
async def on_ready():
    print('Бот загружен')
    print(bot.user)
    if os.environ['IS_HEROKU'] == '1':
        await bot.get_channel(827504142406385664).send(
            embed=discord.Embed(
                description='Бот загружен', 
                timestamp = program_start
            ).set_footer(
                text = bot.command_prefix
            )
        )

if __name__ == '__main__':
    if os.environ['IS_HEROKU'] == '0':
        from dotenv import load_dotenv
        load_dotenv()

    bot.run(os.environ['TOKEN'])