import json
import random
import requests

import discord
from discord.ext import commands
from dislash import *

from TenGiphPy import Tenor
tenor = Tenor('KOVXP2DQ9PU7')


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_commands.command(
        name = 'hug',
        description = 'Обнимает человека',
        guild_ids = [824997091075555419],
        options = [
            Option(
                name = 'target',
                description = 'Тот, кого нужно обнять',
                type = Type.USER,
                required = True
            )
        ]
    )
    async def hug(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} обнял(а) {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime hug'))
        )

    @slash_commands.command(
        name = 'kiss',
        description = 'Целует человека',
        guild_ids = [824997091075555419],
        options = [
            Option(
                name = 'target',
                description = 'Тот, кого нужно поцеловать',
                type = Type.USER,
                required = True
            )
        ]
    )
    async def kiss(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} поцеловал(а) {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime kiss'))
        )
    
    @slash_commands.command(
        name = 'highfive',
        description = 'Дает пять человеку',
        guild_ids = [824997091075555419],
        options = [
            Option(
                name = 'target',
                description = 'Тот, кому нужно дать пять',
                type = Type.USER,
                required = True
            )
        ]
    )
    async def highfive(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} дал(а) пять {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime high five'))
        )

    @slash_commands.command(
        name = 'topic',
        description = 'Рандомная тема чата',
        guild_ids = [824997091075555419]
    )
    async def topic(self, inter):
        result = requests.post(url = 'https://randomall.ru/api/custom/gens/1888')
        if result.status_code == 200:
            decoded = json.loads(result.content.decode('utf8'))
            topics = decoded['msg'].split('\n\n')[:-1]
            await inter.reply(random.choice(topics))
        else:
            await inter.reply(f'response status code: {result.status_code}', ephemeral = True)

def setup(bot):
    bot.add_cog(Fun(bot))
