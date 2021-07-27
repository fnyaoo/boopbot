from os import environ

from tortoise import Tortoise, run_async
from .models import *

# class MemberDB:
#     def __init__(self, member_id) -> None:
#         self.member_id = str(member_id)
    
#     async def fetch(self) -> Members_Super_New:
#         return Members_Super_New.get_or_create(discord_id = self.member_id)[0]

async def _main(db_url):
    await Tortoise.init(
        db_url = db_url,
        modules = {'models': ['utils.db']}
    )
    m = (await models.Members.filter(discord_id = '765197502181277727'))[0]
    print(m.score)

def main():
    if environ.get('DATABASE_URL') is None:
        from dotenv import load_dotenv
        load_dotenv()
    run_async(_main(environ.get('DATABASE_URL')))

if __name__ == '__main__':
    main()