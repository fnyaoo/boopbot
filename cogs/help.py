import discord
from discord.ext import commands
from typing import List

from discord.ext.commands.core import Command

class BotHelpSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, cogs: List[commands.Cog], **options) -> None:
        super().__init__(**options)
        self.mapping = {}

        for cog in cogs:
            emoji_sign = getattr(cog, 'emoji_sign', discord.PartialEmoji(name = 'void', animated = False, id =827958334547951657))
            qualified_name = getattr(cog, '_qualified_name', cog.qualified_name)
            description = getattr(cog, 'description', 'Без описания')
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'

            self.add_option(label = qualified_name, value = cog.qualified_name, description = description, emoji = emoji_sign)
            self.mapping[cog.qualified_name] = cog

    async def callback(self, interaction: discord.Interaction):
        await self.view.help.send_cog_help(self.mapping[self.values[0]], interaction = interaction)

class HelpView(discord.ui.View):
    def __init__(self, user, helpcommand: "MyHelpCommand"):
        super().__init__()
        self.user = user
        self.help = helpcommand
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user
        
class MyHelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.splash = f'https://images-ext-2.discordapp.net/external/Nzf7XfPBxPFWzsf6QKm7EASPu8cUkI-JG0Uxy9Kk_Kw/%3Fsize%3D1024/https/cdn.discordapp.com/splashes/824997091075555419/877b556e3f34f2e63800ba246eb48103.png'
    
    async def send_bot_help(self, mapping):
        mapping.pop(None)
        dest: discord.abc.Messageable = self.get_destination()

        filtered_commands = await self.filter_commands([item for sublist in mapping.values() for item in sublist])
        cog_list = list(filter(
            lambda k: any(command in filtered_commands for command in mapping[k]),
            mapping
        ))

        embed = discord.Embed(
            title = 'Команда помощи',
            color = 0x2f3136,
            description = (
                "Привет! Надеюсь эта команда поможет тебе разобаться во всех командах этого бота. \n"
                "У меня есть пара категорий команд, выбери одну из них в выпадающем списке снизу"
            )
        ).add_field(
            name = 'Доступные категории',
            value = '\n'.join(
                [
                    (
                    f"{getattr(cog, 'emoji_sign', discord.PartialEmoji(name = 'void', animated = False, id =827958334547951657))} "
                    f"{getattr(cog, '_qualified_name', cog.qualified_name)} "
                    f"({cog.qualified_name})"
                    ) for cog in cog_list
                ]
            )
        ).set_image(url=self.splash)
        view = HelpView(self.context.author, self)
        view.add_item(BotHelpSelect(cog_list))
        await dest.send(embed=embed, view=view)

    async def send_cog_help(self, cog: commands.Cog, **kwargs):
        interaction: discord.Interaction = kwargs.get('interaction', None)
        dest = self.get_destination()

        emoji_sign = getattr(cog, 'emoji_sign', None)
        qualified_name = getattr(cog, '_qualified_name', cog.qualified_name)
        description = getattr(cog, 'description', 'Без описания')

        filtered_commands: List[Command] = await self.filter_commands(cog.get_commands())


        embed = discord.Embed(
            title = f'{emoji_sign if emoji_sign else ""} {qualified_name}',
            description = f'Описание категории: {description}',
            color = 0x2f3136
        ).set_image(url=self.splash)
        
        for command in filtered_commands:
            embed.add_field(
                name = f'{self.context.clean_prefix}{command.name}',
                value = command.description or 'Нет описания'
            )
        if interaction is not None:
            await interaction.response.edit_message(embed=embed)
        

class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

        self._qualified_name = 'Помощь'
        self.description = 'Показывает это сообщение'
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot): 
    bot.add_cog(Help(bot))