from bot import BoopBot
from os import environ
from datetime import datetime

from tortoise import Tortoise
from utils import db

environ['IS_HEROKU'] = "1" if 'HEROKU_APP_ID' in environ else "0"

bot = BoopBot()
bot._program_start = datetime.utcnow()

if environ['IS_HEROKU'] == '0':
    from dotenv import load_dotenv
    load_dotenv()

async def main():
    await Tortoise.init(
        db_url = environ.get('DATABASE_URL'),
        modules = {'models': ['utils.db']}
    )
    await Tortoise.generate_schemas()

if __name__ == '__main__':
    bot.loop.run_until_complete(main())
    bot.run(environ.get('TOKEN'))