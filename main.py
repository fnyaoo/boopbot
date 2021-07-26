from bot import BoopBot
from os import environ
from tortoise import Tortoise

environ['IS_HEROKU'] = "1" if 'HEROKU_APP_ID' in environ else "0"


from datetime import datetime
import discord
from discord.ext import commands

from utils import config

bot = BoopBot()
bot._program_start = datetime.utcnow()

async def main():
    await Tortoise.init(
        db_url = environ.get('DB'),
        modules = {'models': ['utils.db']}
    )
    await Tortoise.generate_schemas()


if __name__ == '__main__':
    if environ['IS_HEROKU'] == '0':
        from dotenv import load_dotenv
        load_dotenv()

    bot.loop.run_until_complete(main())
    bot.run(environ.get('TOKEN'))