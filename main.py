from bot import BoopBot
from os import environ
from datetime import datetime

from utils import db

environ['IS_HEROKU'] = "1" if 'HEROKU_APP_ID' in environ else "0"
if environ['IS_HEROKU'] == '0':
    from dotenv import load_dotenv
    load_dotenv()


bot = BoopBot()

if __name__ == '__main__':
    db_url = environ.get('DATABASE_URL')
    token = environ.get('TOKEN')
    bot.loop.run_until_complete(db.main(db_url))
    bot.run(token)