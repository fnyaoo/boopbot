from os import environ

from tortoise import Tortoise, run_async
from tortoise.expressions import F
from .models import *

__all__ = ('main', 'F')

# __models__ = (
#     'Members',
#     'ScoreDailyLog'
# )

async def main(db_url):
    await Tortoise.init(
        db_url = db_url,
        modules = {'models': ['utils.db']}
    )

def sync_main():
    if environ.get('DATABASE_URL') is None:
        from dotenv import load_dotenv
        load_dotenv()
    run_async(main(environ.get('DATABASE_URL')))