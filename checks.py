from discord.ext.commands import check
from discord.ext.commands.errors import NoPrivateMessage

def is_admin():
    async def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()
        return ctx.author.id == 428483942329614336 or 825218095902752768 in [role.id for role in ctx.author.roles]
    return check(predicate)