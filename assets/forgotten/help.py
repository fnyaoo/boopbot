import discord
from discord.ext import commands
from typing import List

from discord.ext.commands.core import Command

class ReturnOption(discord.SelectOption):
    def __init__(self, to: str = 'категориям') -> None:
        super().__init__(label = 'Назад', value = '_back_', description = f'Вернуться к {to}', default = True)

class BotHelpSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, _cogs: List[commands.Cog], **kwargs) -> None:
        super().__init__(**kwargs)
        self.mapping = {}

        for cog in _cogs:
            qualified_name = getattr(cog, '_qualified_name', cog.qualified_name)
            description = getattr(cog, 'description', 'Без описания')
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'
            emoji_sign = getattr(cog, 'emoji_sign', discord.PartialEmoji(name = 'void', animated = False, id = 827958334547951657))

            self.add_option(label = qualified_name, value = cog.qualified_name, description = description, emoji = emoji_sign)
            self.mapping[cog.qualified_name] = cog

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await view.help.send_cog_help(self.mapping[self.values[0]], interaction = interaction)

class CogHelpSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, _commands: List[Command], **kwargs):
        super().__init__(**kwargs)
        self.mapping = {}

        for command in _commands:
            name = command.name
            description = command.description
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'
            self.add_option(label = name, value = name, description = description)
            self.mapping[name] = command
        self.append_option(ReturnOption())
    
    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        view = self.view
        help = view.help

        if value == '_back_':
            view.clear_items()
            view.add_item(BotHelpSelect())
            return help.send_bot_help(help.get_bot_mapping())
        else:
            return help.send_command_help(self.mapping[self.values[0]], interaction = interaction)

class CommandSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, command: Command, **kwargs) -> None:
        super().__init__(**kwargs)
        self.command = command
        self.append_option(ReturnOption(f'команде {command.name}'))
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.clear_items()
        help = view.help
        cog: commands.Cog = self.command.cog
        filtered_commands = help.filter_commands(cog.get_commands())
        view.add_item(CogHelpSelect(filtered_commands))
        return help.send_cog_help(self.command.cog)

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
        self.init_message = None

    async def send_bot_help(self, mapping, **kwargs):
        interaction: discord.Interaction = kwargs.get('interaction', None)
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
        self.view = HelpView(self.context.author, self)
        self.view.add_item(BotHelpSelect(cog_list))
        if interaction is None:
            if self.init_message is None:
                self.init_message = await dest.send(embed=embed, view=self.view)
            else:
                await self.init_message.edit(embed=embed, view=self.view)
        else:
            await interaction.response.edit_message(embed=embed, view=self.view)

    async def send_cog_help(self, cog: commands.Cog, **kwargs):
        interaction: discord.Interaction = kwargs.get('interaction', None)

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
        if interaction is None:
            await self.init_message.edit(embed=embed, view=self.view)
        else:
            await interaction.response.edit_message(embed=embed, view=self.view)
        
    async def send_command_help(self, command: Command, **kwargs):
        interaction: discord.Interaction = kwargs.get('interaction', None)

        embed = discord.Embed(
            title = f'Команда {command.name}',
            description = command.description or 'Нет описания',
            color = 0x2f3136
        )
        if len(command.aliases) > 0:
            embed.add_field(
                name = 'Псевдонимы',
                value = ', '.join(command.aliases)
            )
        embed.add_field(
            name = 'Сигнатура',
            value = 'self.get_command_signature(command)'
        )
        if interaction is None:
            await self.init_message.edit(embed=embed)


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