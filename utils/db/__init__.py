from os import environ

from tortoise import Tortoise, run_async
from .models import *

# class MemberDB:
#     def __init__(self, member_id) -> None:
#         self.member_id = str(member_id)
    
#     async def fetch(self) -> Members_Super_New:
#         return Members_Super_New.get_or_create(discord_id = self.member_id)[0]

async def main(db_url):
    await Tortoise.init(
        db_url = db_url,
        modules = {'models': ['utils.db']}
    )

if __name__ == '__main__':
    if environ.get('DATABASE_URL') is None:
        from dotenv import load_dotenv
        load_dotenv()
    run_async(main(environ.get('DATABASE_URL')))