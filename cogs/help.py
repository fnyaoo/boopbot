import discord
from discord.ext import commands


class MyHelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.splash = f'https://images-ext-2.discordapp.net/external/Nzf7XfPBxPFWzsf6QKm7EASPu8cUkI-JG0Uxy9Kk_Kw/%3Fsize%3D1024/https/cdn.discordapp.com/splashes/824997091075555419/877b556e3f34f2e63800ba246eb48103.png'
    
    async def send_bot_help(self, mapping):
        dest: discord.abc.Messageable = self.get_destination()

        filtered_commands = await self.filter_commands(flat_list = [item for sublist in mapping.values() for item in sublist])
        cog_list = list(filter(
            lambda k: (
                mapping[k] != [] and 
                any(command in filtered_commands for command in mapping[k])
            ), 
            mapping
        ))

        embed = discord.Embed(
            title = 'Команда помощи',
            color = 0x2f3136,
            description = (
                "Привет! Надеюсь эта команда поможет тебе разобаться во всех особенностях этого бота. \n"
                "У меня есть пара категорий команд, выбери одну из них в выпадающем списке снизу"
            )
        ).set_image(
            url=self.splash
        ).add_field(
            name = 'Доступные категории',
            value = '\n'.join([f"**{cog._qualified_name}**" for cog in cog_list])
        )
        await dest.send(embed=embed)
        
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
