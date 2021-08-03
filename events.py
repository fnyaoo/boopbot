import discord
from discord.ext import commands
from utils import config

roles = {
    '🦑','👛','🏮','👌🏻','🌆',
    '📒','🍌','🍃','🐢','📗',
    '🧪','🩲','🌊','🧿','🔮',
    '🍆','🌺','🦔','💿','♟️'
}

def setup(bot: commands.Bot):

    async def log_delete(message):
        if message.author.id == 234395307759108106: return
        if message.channel.id == 827611418286358540: return

        bot.dispatch('log_message_delete', message)
    bot.add_listener(log_delete, 'on_message_delete')
    
    async def log_edit(before, after):
        if before.author.id == 234395307759108106: return
        if before.author.id == bot.user.id:        return
        if before.content == after.content:        return
    
        bot.dispatch('log_message_edit', before, after)
    bot.add_listener(log_edit, 'on_message_edit')
    
    async def log_voice(member, before, after):
        if before.channel == after.channel: return
        if after.channel:
            if after.channel.id == 831396453545017384: return
        
        if (not before.channel) and after.channel:   color = 0xa1ea8f
        elif before.channel and after.channel:       color = 0xff8348
        elif before.channel and (not after.channel): color = 0xff7772
        else:                                        color = 0xffffff

        bot.dispatch('log_voice_state_update', member, before, after, color)
    bot.add_listener(log_voice, 'on_voice_state_update')

    async def add_color(payload: discord.RawReactionActionEvent):
        if payload.message_id !=  833406896072949790:
            return
        if not payload.emoji.name in roles:
            return
        if payload.member.id == bot.user.id:
            return
        member = bot.get_guild(824997091075555419).get_member(payload.user_id)

        bot.dispatch('add_color', member, payload.emoji.name)

    bot.add_listener(add_color, 'on_raw_reaction_add')

    async def remove_color(payload: discord.RawReactionActionEvent):
        if not payload.message_id == 833406896072949790:
            return
        if not payload.emoji.name in roles:
            return
        member = bot.get_guild(824997091075555419).get_member(payload.user_id)

        bot.dispatch('remove_color', member, payload.emoji.name)
    bot.add_listener(remove_color, 'on_raw_reaction_remove')

    async def role_update(before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            return
        if (set(before.roles).symmetric_difference(set(after.roles))[0]).id in config['delimiter']['roles'].values():
            return

        bot.dispatch('role_update', after)
    bot.add_listener(role_update, 'on_member_update')