import re
import random
import asyncio

import discord
from discord.ext import commands, tasks

from utils import inflect_by_amount, levels, levels_inverted, get_level, get_next, BarCreator
from utils.db import Members, F
from utils.menus import ScoringPages



class ScoringSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        bot.in_active = {}

        self._qualified_name = 'Активность в чате'
        self.description = 'Скоринг-система и команды взаимодействия с ней.'


    @commands.Cog.listener()
    async def on_message(self, message):
        if  message.content.startswith(('l!', 't!', '!', '-')) or \
            message.author.bot or \
            message.author.id in self.bot.in_active or \
            (not message.channel.id in [824997091725017090]): 
            return
        self.bot.in_active[message.author.id] = {'streak': 0, 'last': message.created_at}

        def clean(content: str):
            new_ct = re.sub('<(?:@|#|:\S+:|@&)\d{18}>', '', content)
            new_ct = re.sub('[^a-zA-Zа-яА-ЯёЁ]', '', new_ct)
            return new_ct

        # new method
        handmember = self.bot.in_active[message.author.id]
        
        try:
            while True:
                latest = await self.bot.wait_for(
                    'message', 
                    check = lambda m: m.author == message.author and m.channel == message.channel, 
                    timeout = 80
                )

                if (latest.created_at - handmember['last']).total_seconds() < 40:
                    continue
                if latest.content.startswith(('l!', 't!', '!', '-')):
                    continue

                handmember['last'] = latest.created_at
                member, _ = await Members.get_or_create(discord_id = str(message.author.id))

                if len(clean(latest.content)) > 4 and len(self.bot.in_active) > 1:
                    await Members.filter(discord_id=str(message.author.id)).update(score = F('score') + 1)
                    handmember['streak'] += 1
                    
                    await member.refresh_from_db(('score',))
                    if member.score in levels:
                        await latest.reply(
                            embed = discord.Embed(
                                title = f'🎉 {random.choice(("Конгратс!", "Поздравляем!"))}',
                                description = (
                                    f'{latest.author.mention} получил(а) '
                                    f'{levels[member.score]}-й уровень, '
                                    f'набрав {inflect_by_amount(member.score, "очко")}'
                                ),
                                color = 0xffc83d
                            )
                        )

        except asyncio.TimeoutError:
            self.bot.in_active.pop(message.author.id)

       # old method
        # xp = len(new_ct)
        # xp = xp if xp <= 15 else 15
        # if xp > 3:
        #     modal = m(message.author)
        #     json: dict = modal.member.json
        #     score_row = json.get('score')
        #     if score_row:
        #         last = dt.fromisoformat(score_row['last'])
        #         if (message.created_at - last).total_seconds() > 3:
        #             score_row['total'] += xp
        #             score_row['last'] = message.created_at.isoformat()
        #         else: ...
        #     else:
        #         json['score'] = {'total': xp, 'last': message.created_at.isoformat()}
        #     modal.save()
       #

    @commands.group(name = 'score', invoke_without_command = True)
    async def _score(self, ctx: commands.Context, target: discord.Member = None):
        target = target or ctx.author
        member = await Members.get_or_create(discord_id=str(target.id))
        member = member[0]
        xp = member.score
        current_level = get_level(xp)
        current_next = get_next(xp)

        bh = BarCreator(levels_inverted[current_level], levels_inverted[current_level+1], xp)

        embed = discord.Embed(
        ).set_author(
            name = f'{target.display_name} | Активность в чате',
            icon_url = target.avatar.url
        ).add_field(
            name = 'Уровень',
            value = f'```diff\n- {current_level}-й уровень\n```'
        ).add_field(
            name = 'Все очки',
            value = f'```fix\n# {inflect_by_amount(xp, "очко")}\n```'
        ).add_field(
            name = 'До следующего уровня',
            value = f'```diff\n+ {inflect_by_amount(current_next-xp, "очко")}\n```'
        ).add_field(
            name = 'Прогресс',
            value = f'```{bh.bar()}| {current_level+1}lvl ({bh.persent}%)```',
            inline = False
        )
        if ctx.author.id in self.bot.in_active:
            handmember = self.bot.in_active[ctx.author.id]
            embed.set_footer(text = f'last: {handmember["last"].time()}\nstreak: {handmember["streak"]}')
        await ctx.send(embed = embed)
    
    @_score.command(name = 'top')
    async def _top(self, ctx):
        query = (Members
            .exclude(score = 0)
            .order_by('-score')
        )
        menu = ScoringPages(await query)
        await menu.start(ctx)

def setup(bot):
    bot.add_cog(ScoringSystem(bot))
