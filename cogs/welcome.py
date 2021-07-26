import discord
from discord.ext import commands

from utils.menus import GateMenu


class Welcomer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    async def get_invites(self):
        return sorted(await self.guild.invites(), key = lambda inv: inv.code)

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(824997091075555419)
        self.gate_cat = self.bot.get_channel(843867667551092757)
        self.invites = await self.get_invites()
        self.bup = self.guild.get_role(824997272537661470)
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        before = await before.invites()
        after = await after.invites()
        if before == after:
            return
        self.invites = await self.get_invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        new_invites = await self.get_invites()
        couched = None
        for i in range(len(new_invites)):
            try:
                if self.invites[i].uses != new_invites[i].uses:
                    couched = new_invites[i]
                    break
            except: pass

        emb = discord.Embed(
            title = f'Привет, незнакомец!',
            description = f'Здесь ты можешь рассказать о себе, чтобы мы могли понять, ' \
                            f'стоит тебя впускать, или нет.',
            color = 0x6a3eb8
        )
        if couched:
            emb.add_field(
                name = 'Информация об инвайте',
                value = f'>>> Создатель инвайта: {couched.inviter.mention}\nКол-во использований: `{couched.uses}`\nКод: `{couched.code}`'
            )

        o = self.gate_cat.overwrites.copy()
        o[member] = discord.PermissionOverwrite(
            read_message_history = True,
            read_messages = True,
            send_messages = True
        )
        gate = await self.gate_cat.create_text_channel(f'врата-{member.id}', overwrites = o)
        # await gate.send(f'{member.mention}<@&825218095902752768>', delete_after = 0.1)

        menu_message = await gate.send(embed = emb)
        result = await GateMenu(menu_message, [490863657740271628, 428483942329614336, 344781718491889664]).reconst(await self.bot.get_context(menu_message))
        if result:
            await member.add_roles(self.bup)
        else:
            await member.kick()
        await gate.delete()

def setup(bot):
    bot.add_cog(Welcomer(bot))
