import discord
from discord.ext import commands


class MyHelpCommand(commands.HelpCommand): ...

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