import json
import random
import requests

import discord
import dislash
from discord.ext import commands
from dislash import application_commands, Option, OptionType, OptionChoice
from akinator.async_aki import Akinator

from TenGiphPy import Tenor
tenor = Tenor('KOVXP2DQ9PU7')

guilds = [
    824997091075555419,
    # 859290967475879966,
]


class ChoiceSelect(discord.ui.Select):
    view: 'AkiChoiceView'
    button_args = [
        {'value': 'yes', 'label': 'Да'},
        {'value': 'no', 'label': 'Нет'},
        {'value': 'idk', 'label': 'Не знаю'},
        {'value': 'probably', 'label': 'Возможно'},
        {'value': 'probably not', 'label': 'Скорее нет'}
    ]

    def __init__(self) -> None:
        super().__init__(custom_id = 'suggest', placeholder = 'Сделайте выбор', options = [
            discord.SelectOption(**button)
            for button in self.button_args
        ])
    
    async def callback(self, interaction: discord.Interaction):
        aki = self.view.client

        await aki.answer(self.values[0])
        if aki.progression < 90:
            embed = self.view.make_embed()
        else:
            await aki.win()
            self.view.stop()
            self.view.clear_items()
            embed = self.view.final_embed()

        await interaction.response.edit_message(embed = embed, view = self.view)


class AkiChoiceView(discord.ui.View):
    def __init__(self, author: discord.Member, aki_client: Akinator):
        super().__init__(timeout = None)
        self.client = aki_client
        self.author = author
        self.add_item(ChoiceSelect())

    def make_embed(self):
        return discord.Embed(
            description = self.client.question,
            color = 0xa3b8ee
        ).set_author(
            name = self.author.display_name,
            icon_url = self.author.avatar.url
        )

    def final_embed(self):
        guess = self.client.first_guess
        return discord.Embed(
            description = f'Это же {guess["name"]} ({guess["description"]})!'
        ).set_image(
            url = guess['absolute_picture_path']
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message('Вы не автор сообщения', ephemeral = True)
            return False
        return True



class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @application_commands.slash_command(
        name = 'hug',
        description = 'Обнимает человека',
        guild_ids = guilds,
        options = [
            Option(
                name = 'target',
                description = 'Тот, кого нужно обнять',
                type = OptionType.USER,
                required = True
            )
        ]
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _slash_hug(self, inter, target):
        await self.hug(inter, target)


    @application_commands.user_command(
        name = 'Обнять',
        guild_ids = guilds
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _user_hug(self, inter):
        await self.hug(inter, inter.member)


    async def hug(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} обнял(а) {target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime hug'))
        )


    @application_commands.slash_command(
        name = 'kiss',
        description = 'Целует человека',
        guild_ids = guilds,
        options = [
            Option(
                name = 'target',
                description = 'Тот, кого нужно поцеловать',
                type = OptionType.USER,
                required = True
            )
        ]
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _slash_kiss(self, inter, target):
        await self.kiss(inter, target)


    @application_commands.user_command(
        name = 'Поцеловать',
        guild_ids = guilds
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _user_kiss(self, inter):
        await self.kiss(inter, inter.member)


    async def kiss(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} поцеловал(а) {target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime kiss'))
        )


    @application_commands.slash_command(
        name = 'highfive',
        description = 'Дает пять человеку',
        guild_ids = guilds,
        options = [
            Option(
                name = 'target',
                description = 'Тот, кому нужно дать пять',
                type = OptionType.USER,
                required = True
            )
        ]
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _slash_highfive(self, inter, target):
        await self.highfive(inter, target)


    @application_commands.user_command(
        name = 'Дать пять',
        guild_ids = guilds
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _user_highfive(self, inter):
        await self.highfive(inter, inter.member)


    async def highfive(self, inter, target):
        await inter.reply(
            f'{inter.author.mention} дал(а) пять {target.mention}', 
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom('anime high five'))
        )


    @application_commands.slash_command(
        name = 'bonk',
        description = 'Дает пизды человеку',
        guild_ids = guilds,
        options = [
            Option(
                name = 'target',
                description = 'Тот, кому нужно дать пизды',
                type = OptionType.USER,
                required = True
            )
        ]
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _slash_bonk(self, inter, target):
        await self.bonk(inter, target)


    @application_commands.user_command(
        name = 'Дать пизды',
        guild_ids = guilds
    )
    @application_commands.cooldown(1, 300, commands.BucketType.user)
    async def _user_bonk(self, inter):
        await self.bonk(inter, inter.member)


    async def bonk(self, inter, target):
        ch = ['bonk', 'boxing', 'fight']
        await inter.reply(
            f'{inter.author.mention} ёбнул(а) {target.mention}',
            embed = discord.Embed(color = 0x2f3136).set_image(url = await tenor.arandom(f'anime {random.choice(ch)}'))
        )


    @application_commands.slash_command(
        name = 'topic',
        description = 'Рандомная тема чата',
        guild_ids = guilds
    )
    @application_commands.cooldown(1, 300, commands.BucketType.channel)
    async def topic(self, inter):
        result = requests.post(url = 'https://randomall.ru/api/custom/gens/1888')
        if result.status_code == 200:
            decoded = json.loads(result.content.decode('utf8'))
            topics = decoded['msg'].split('\n\n')[:-1]
            await inter.reply(random.choice(topics))
        else:
            await inter.reply(f'response status code: {result.status_code}', ephemeral = True)


    @application_commands.slash_command(
        name = 'akinator',
        description = 'Игра "Акинатор"',
        guild_ids = guilds,
        options = [
            Option(
                'language', 'Язык вопросов акинатора (русский по умолчанию)',
                choices = [
                    OptionChoice('Русский', 'ru'),
                    OptionChoice('English', 'en'),
                    OptionChoice('English for guessing animals', 'en_animals'),
                    OptionChoice('English for guessing objects', 'en_objects')
                ]
            )
        ]
    )
    @application_commands.is_owner()
    # @application_commands.cooldown(1, 120, commands.BucketType.user)
    async def _akinator(self, inter: dislash.SlashInteraction, language = None):
        language = language or 'ru'
        aki = Akinator()
        await aki.start_game(language)
        view = AkiChoiceView(inter.author, aki)
        await inter.reply(embed = view.make_embed(), view = view)

        await view.wait()
        await aki.close()

def setup(bot):
    bot.add_cog(Fun(bot))
