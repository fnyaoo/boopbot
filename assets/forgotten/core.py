from datetime import datetime

import discord
from discord.ext import commands
from discord.http import Route

# from cogs.utils.funcs import config


program_start = datetime.utcnow()
bot = commands.Bot(
    '`~`',
    intents = discord.Intents.all()
)

bot.load_extension('jishaku')

@bot.event
async def on_ready():
    print('Bot is ready!')
    print(bot.user)

@bot.command()
@commands.is_owner()
async def test(ctx):
    await bot.http.request(
        Route('POST', f'/channels/{ctx.channel.id}/messages'),
        json = {
            'content': 'test',
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "style": 1,
                            "custom_id": "previous_page",
                            "label": "◀️ Previous Page"
                        },
                        {
                            "type": 2,
                            "style": 4,
                            "custom_id": "close",
                            "label": "❌ Close Menu"
                        },
                        {
                            "type": 2,
                            "style": 1,
                            "custom_id": "next_page",
                            "label": "▶️ Next Page"
                        }
                    ]
                }
            ]
        }
    )
bot.run('ODQ2NzMwNTI3NjgzMjQ4MTM5.YKzxQQ.eNXblFXXekX1CXh40ieHc63uZI4')