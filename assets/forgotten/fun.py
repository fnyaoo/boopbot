import json
import random
import requests

import discord
from discord.ext import commands
from dislash import slash_commands

from TenGiphPy import Tenor
tenor = Tenor('KOVXP2DQ9PU7')


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_commands.command(
        name = 'hug',
        description = 'Обнимает человка',
        guild_ids = [824997091075555419],
        options = [
            slash_commands.Option(
                name = 'target',
                description = 'Тот, кого нужно обнять',
                type = slash_commands.Type.USER,
                required = True
            )
        ]
    )
    async def hug(self, inter):
        target = inter.get('target')
        if not target:
            return await inter.reply('Нельзя никого не обнимать!')
        await inter.reply(
            f'{inter.author.mention} обнял(а) {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0xf0f0f0).set_image(url = tenor.random('anime hug'))
        )

    @slash_commands.command(
        name = 'kiss',
        description = 'Целует человка',
        guild_ids = [824997091075555419],
        options = [
            slash_commands.Option(
                name = 'target',
                description = 'Тот, кого нужно поцеловать',
                type = slash_commands.Type.USER,
                required = True
            )
        ]
    )
    async def kiss(self, inter):
        target = inter.get('target')
        if not target:
            return await inter.reply('Нельзя никого не целовать!')
        await inter.reply(
            f'{inter.author.mention} поцеловал(а) {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0xf0f0f0).set_image(url = tenor.random('anime kiss'))
        )
    
    @slash_commands.command(
        name = 'highfive',
        description = 'Дает пять человеку',
        guild_ids = [824997091075555419],
        options = [
            slash_commands.Option(
                name = 'target',
                description = 'Тот, кому нужно дать пять',
                type = slash_commands.Type.USER,
                required = True
            )
        ]
    )
    async def highfive(self, inter):
        target = inter.get('target')
        if not target:
            return await inter.reply('Нельзя дать пять воздуху!')
        await inter.reply(
            f'{inter.author.mention} дал(а) пять {target if target is str else target.mention}', 
            embed = discord.Embed(color = 0xf0f0f0).set_image(url = tenor.random('anime high five'))
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
