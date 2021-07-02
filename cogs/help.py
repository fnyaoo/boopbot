from typing import List, NamedTuple, Optional, TypeVar, Union
import discord
from discord.ext import commands
from discord.ext.commands.core import Command, Group


Mapping = dict[Optional[commands.Cog], Command]

class CogRepr(NamedTuple):
    emoji: str
    relevant: str
    class_name: str
    cog: commands.Cog

    @property
    def merged(self):
        return f'{self.emoji} {self.relevant} ({self.class_name})'

def cog_qualifided(cogs):
    def foo(cog):
        return CogRepr(
            emoji = getattr(cog, 'emoji_sign', str(discord.PartialEmoji(name = 'void', animated = False, id =827958334547951657))),
            relevant = getattr(cog, '_qualified_name', cog.qualified_name),
            class_name = cog.qualified_name,
            cog = cog)
    if isinstance(cogs, list):
        return [foo(cog) for cog in cogs]
    else:
        return foo(cogs)

def help_view(func):
    def wrapper(self, *args, **kwargs):
        if self.view is None:
            self.view = HelpView(self.context.author, self)
        return func(self, *args, **kwargs)
    return wrapper


class ReturnOption(discord.SelectOption):
    VALUE = 'BACK'
    def __init__(self, to: str) -> None:
        super().__init__(label = 'Назад', value = self.VALUE, description = f'Вернуться к {to}')
class ReturnButton(discord.ui.Button):
    VALUE = 'BACK'
    view: "HelpView"

    def __init__(self, back_to):
        super().__init__(
            style     = discord.ButtonStyle.gray, 
            label     = "Назад", 
            custom_id = self.VALUE, 
            emoji     = '🔙'
        )
        self.back_to = back_to
    async def callback(self, interaction: discord.Interaction):
        help = self.view.help
        for type, coro in zip(
            [dict, commands.Cog, Group, Command],
            [help.send_bot_help, help.send_cog_help, help.send_group_help, help.send_command_help]
        ):
            if isinstance(self.back_to, type):
                return await coro(self.back_to, interaction)


class BotSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, cog_list: List[commands.Cog]) -> None:
        super().__init__(custom_id='cog_selection', placeholder='Выберите категорию')
        self.cog_mapping = {}
        
        for cog_repr in cog_qualifided(cog_list):
            description = getattr(cog_repr.cog, 'description', 'Без описания')
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'
            
            self.add_option(
                label = cog_repr.relevant,
                value = cog_repr.class_name,
                description = description,
                emoji = cog_repr.emoji
            )
            self.cog_mapping[cog_repr.class_name] = cog_repr.cog
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await view.help.send_cog_help(self.cog_mapping[self.values[0]], interaction)

class CogSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, command_list: List[Command]) -> None:
        super().__init__(custom_id='command_selection', placeholder='Выберите команду')
        self.command_mapping = {}

        for command in command_list:
            name = command.name
            description = command.description or 'Нет описания'
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'
            
            self.add_option(
                label = name,
                value = name,
                description = description
            )
            self.command_mapping[name] = command
        self.append_option(ReturnOption('категориям'))

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        view = self.view
        help = view.help

        if value == ReturnOption.VALUE:
            await help.send_bot_help(help.get_bot_mapping(), interaction)
        else:
            command = self.command_mapping[value]
            if isinstance(command, Group):
                await help.send_group_help(command, interaction)
            else:
                await help.send_command_help(command, interaction)

class GroupSelect(discord.ui.Select):
    view: "HelpView"

    def __init__(self, command_list: List[Union[Group, Command]]) -> None:
        super().__init__(custom_id='group_commands_selection', placeholder='Выберите команду')
        self.command_mapping = {}
        self.current_page = None

        for command in command_list:
            name = command.name
            description = command.description or 'Нет описания'
            if len(description) > 50:
                description = description[:-(len(description)-47)] + '...'
            
            self.add_option(
                label = name,
                value = name,
                description = description
            )
            self.command_mapping[name] = command
        self.append_option(ReturnOption('категории'))
    
    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        view = self.view
        help = view.help

        if value == ReturnOption.VALUE:
            await help.send_bot_help(help.get_bot_mapping(), interaction)
        else:
            command = self.command_mapping[value]
            if isinstance(command, Group):
                await help.send_group_help(command, interaction)
            else:
                await help.send_command_help(command, interaction)

class HelpView(discord.ui.View):
    def __init__(self, user: discord.abc.User, helpcommand: "MyHelpCommand"):
        super().__init__()
        self.user = user
        self.help = helpcommand
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user


class MyHelpCommand(commands.HelpCommand):
    context: commands.Context
    view: HelpView

    def __init__(self, **options):
        super().__init__(**options)
        self.image = f'https://images-ext-2.discordapp.net/external/Nzf7XfPBxPFWzsf6QKm7EASPu8cUkI-JG0Uxy9Kk_Kw/%3Fsize%3D1024/https/cdn.discordapp.com/splashes/824997091075555419/877b556e3f34f2e63800ba246eb48103.png'
        self.message = None
        self._commands = None
        self.view = None

    @property
    async def cache_commands(self):
        mapping = self.get_bot_mapping()
        mapping.pop(None)
        self._commands = await self.filter_commands([item for sublist in mapping.values() for item in sublist])
        return self._commands
    
    async def filter_cog_commands(self, cog: commands.Cog):
        return await self.filter_commands(cog.get_commands())

    def cogs_from_commands(self, mapping: Mapping, commands: List[Command]):
        return list(filter(
            lambda k: any(command in commands for command in mapping[k]),
            mapping
        ))

    async def send_help(self, embed: discord.Embed, interaction: discord.Interaction = None):
        if interaction is None:
            if self.message is None:
                dst: discord.abc.Messageable = self.get_destination()
                self.message = await dst.send(embed=embed, view=self.view)
            else:
                await self.message.edit(embed=embed, view=self.view)
        else:
            await interaction.response.edit_message(embed=embed, view=self.view)


    @help_view
    async def send_bot_help(self, mapping: Mapping, interaction: discord.Interaction = None):
        mapping.pop(None)
        cog_list = self.cogs_from_commands(mapping, await self.cache_commands)

        embed = discord.Embed(
            title = 'Команда помощи',
            color = 0x2f3136,
            description = (
                "Привет! Надеюсь эта команда поможет тебе разобаться во всех командах этого бота. "
                "У меня есть пара категорий команд, выбери одну из них в выпадающем списке снизу."
            )
        ).add_field(
            name = 'Доступные категории',
            value = '\n'.join(
                [cog_repr.merged for cog_repr in cog_qualifided(cog_list)]
            ) or 'Нет доступных категорий'
        ).set_image(url=self.image)

        self.view.clear_items()
        self.view.add_item(BotSelect(cog_list))
        
        await self.send_help(embed, interaction)

    @help_view
    async def send_cog_help(self, cog: commands.Cog, interaction: discord.Interaction = None):
        command_list: List[Command] = await self.filter_commands(cog.get_commands())

        embed = discord.Embed(
            title = cog_qualifided(cog).merged,
            description = cog.description,
            color = 0x2f3136
        )
        for command in command_list:
            embed.add_field(
                name = f'{self.context.clean_prefix}{command.name}',
                value = command.description or 'Нет описания'
            )
        
        self.view.clear_items()
        self.view.add_item(CogSelect(command_list))

        await self.send_help(embed, interaction)
    
    @help_view
    async def send_command_help(self, command: Command, interaction: discord.Interaction = None):
        parents: List[Group] = command.parents
        command.full_parent_name
        back_to = None

        embed = discord.Embed(
            title = f'Команда {command.name}',
            description = command.description or 'Нет описания',
            color = 0x2f3136
        ).add_field(
            name = 'Сигнатура',
            value = self.get_command_signature(command),
            inline = False
        )
        if command.cog is not None:
            back_to = command.cog
            embed.add_field(
                name = 'Категория',
                value = cog_qualifided(command.cog).merged
            )
        if command.full_parent_name:
            back_to = parents[0]
            embed.add_field(
                name = 'Родители',
                value = command.full_parent_name
            )
        if len(command.aliases) > 0:
            embed.add_field(
                name = 'Другие названия',
                value = ', '.join(command.aliases) or 'Отсутствует'
            )
        
        self.view.clear_items()
        self.view.add_item(ReturnButton(back_to or self.get_bot_mapping()))

        await self.send_help(embed, interaction)
    
    @help_view
    async def send_group_help(self, group: Group, interaction: discord.Interaction = None):
        command_list: List[Command] = await self.filter_commands(list(group.commands))
        parents = group.parents

        embed = discord.Embed(
            title = f'Группа комманд {group.name}',
            description = group.description or 'Нет описания',
            color = 0x2f3136
        ).add_field(
            name = 'Сигнатура',
            value = self.get_command_signature(group)
        ).add_field(
            name = 'Команды',
            value = '\n'.join(
                [
                    f"{self.context.clean_prefix}"
                    f"{group.full_parent_name+ (' ' if group.full_parent_name else '')}"
                    f"{group.name} {cmd.name}{f' – {cmd.description}' if cmd.description else ''}" 
                    for cmd in command_list
                ]
            ),
            inline = False
        )
        if group.cog is not None:
            embed.add_field(
                name = 'Категория',
                value = cog_qualifided(group.cog).merged
            )
        if len(parents) > 0:
            embed.add_field(
                name = 'Родители',
                value = ' '.join([parent.name for parent in parents[:-1]])
            )
        if len(group.aliases) > 0:
            embed.add_field(
                name = 'Другие названия',
                value = ', '.join(group.aliases)
            )
        
        self.view.clear_items()
        self.view.add_item(GroupSelect(command_list))

        await self.send_help(embed, interaction)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

        self._qualified_name = 'Помощь'
        self.description = 'Показывает это сообщение'
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot): 
    bot.add_cog(Help(bot))