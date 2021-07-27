import discord
from discord.ext import commands


class ColorChanger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self._qualified_name = 'Цвета'
        self.description = 'Команды, связванные с разработкой цветов'

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(827470485604401192)

        self.roles = {
            '🦑': 833053374600577026,
            '👛': 833053402405142538,
            '🏮': 833053432234901505,
            '👌🏻': 833235083355095082,
            '🌆': 833053576745451613,
            '📒': 833053452405571604,
            '🍌': 833053536245383238,
            '🍃': 833053525432860692,
            '🐢': 833053547142709319,
            '📗': 833053557347450901,
            '🧪': 833232827134246952,
            '🩲': 833231105385562142,
            '🌊': 833053748380827649,
            '🧿': 833053502833950730,
            '🔮': 833053757498982500,
            '🍆': 833238131964379166,
            '🌺': 833053319218855966,
            '🦔': 833065024091848724,
            '💿': 833053569304494136,
            '♟️': 833053487033090058,
        }

        for key, value in self.roles.items():
            self.roles[key] = channel.guild.get_role(value)

        self.message: discord.Message = await channel.fetch_message(833406896072949790)
    
    @commands.Cog.listener()
    async def on_add_color(self, member, emoji):
        user_roles = list(filter(lambda x: x.name in self.roles, member.roles))
        if len(user_roles) > 0:
            for role in user_roles:
                reaction = discord.utils.get(self.message.reactions, emoji = role.name)
                if reaction is not None:
                    await reaction.remove(member)

        new_role = self.roles[emoji]
        await member.add_roles(new_role)
    
    @commands.Cog.listener()
    async def on_remove_color(self, member, emoji):
        role = self.roles[emoji]
        if role in member.roles:
            await member.remove_roles(role)
        
    @commands.command(name = 'color_resend')
    @commands.is_owner()
    async def embed_resend(self, ctx):
        text =   '<@&833053374600577026> — Кальмар' \
               '\n<@&833053402405142538> — Коралловый' \
               '\n<@&833053432234901505> — Красный фонарь' \
               '\n<@&833235083355095082> — Бежевый' \
               '\n<@&833053576745451613> — Закат' \
               '\n<@&833053452405571604> — Золотой' \
               '\n<@&833053536245383238> — Я – банан' \
               '\n<@&833053525432860692> — No Drugs For Today' \
               '\n<@&833053547142709319> — Черепаха Наталия' \
               '\n<@&833053557347450901> — Изумрудный' \
               '\n<@&833232827134246952> — Прививка от короны' \
               '\n<@&833231105385562142> — Пантсу' \
               '\n<@&833053748380827649> — Морская волна' \
               '\n<@&833053502833950730> — Синий глаз' \
               '\n<@&833053757498982500> — Я знаю, что вы делали этим летом' \
               '\n<@&833238131964379166> — Баклажан' \
               '\n<@&833053319218855966> — Гибискус' \
               '\n<@&833065024091848724> — Подпарашный ёжик' \
               '\n<@&833053569304494136> — Легендарная пыль' \
               '\n<@&833053487033090058> — Тень'
        msg = await ctx.send(embed = discord.Embed(description = text))
        for emoji in self.roles:
            await msg.add_reaction(emoji)


def setup(bot):
    bot.add_cog(ColorChanger(bot))
