from discord.ext import commands, tasks

from mcstatus import MinecraftServer
from rcon import rcon


class ServerStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = MinecraftServer.lookup("135.181.126.170:25913")
        self.last_lookup = None


    @tasks.loop(seconds=30)
    async def online_checker(self):
        peoples = self.server.status().players.online
        new_name = f'Онлайн: {peoples}'
        if self.last_lookup != peoples and self.category.name != new_name:
            await self.category.edit(name=new_name)
            self.last_lookup = peoples
        
        query = self.server.query()
        last_names = [cnl.name for cnl in self.category.channels]
        names = query.players.names
        delete = list(set(last_names) - set(names))
        create = list(set(names) - set(last_names))
        for name in delete:
            cnl = list(filter(lambda channel: channel.name == name, self.category.channels))[0]
            await cnl.delete()
        for name in create:
            await self.category.create_voice_channel(name)

    @commands.Cog.listener()
    async def on_ready(self):
        self.category = self.bot.get_channel(839526303065571358)
        for channel in self.category.channels: 
            await channel.delete()
        self.online_checker.start()

    @commands.command(name='rcon')
    @commands.is_owner()
    async def exec_rcon(self, ctx, command, *, args=None):
        if args is not None:
            args = args.split(' ')
            response = await rcon(command, *args, 
                                  host='135.181.126.170', port=25575, passwd='0ko65Uvy')
        else:
            response = await rcon(command, 
                                  host='135.181.126.170', port=25575, passwd='0ko65Uvy')
        await ctx.send(f'```nim\n{response}\n```')

def setup(bot):
    bot.add_cog(ServerStatus(bot))
