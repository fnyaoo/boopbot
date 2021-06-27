import asyncio
import aiohttp

async def main(token):
    async with aiohttp.ClientSession() as session:
        session.post(
            url = 'https://discord.com/api/v6/',
            header = f'Authorization: Bot '
        )