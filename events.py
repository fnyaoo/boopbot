from discord.ext import commands

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
    
    