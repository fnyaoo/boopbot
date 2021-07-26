import re
import random
import asyncio

import discord
from discord.ext import commands, tasks

from utils.db import MemberDB, Scoring
from utils import inflect_by_amount, levels, levels_inverted, get_level, BarCreator, config
from utils.menus import ScoringPages



class ScoringSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        self.handled = {}
        self.score_client = Scoring

        self._qualified_name = 'Активность в чате'
        self.description = 'Скоринг-система и команды взаимодействия с ней.'


    @commands.Cog.listener()
    async def on_message(self, message):
        if  message.content.startswith(('l!', 't!', '!', '-')) or \
            message.author.bot or \
            message.author.id in self.handled or \
            (not message.channel.id in [824997091725017090]): 
            return
        self.handled[message.author.id] = {'st': 0, 'l': message.created_at}

        def clean(content: str):
            new_ct = re.sub('<(?:@|#|:\S+:|@&)\d{18}>', '', content)
            new_ct = re.sub('[^a-zA-Zа-яА-ЯёЁ]', '', new_ct)
            return new_ct

        # new method
        member = await MemberDB(message.author.id).fetch()
        handmember = self.handled[message.author.id]
        
        try:
            while True:
                limits = config.values['xp']['limits']
                latest = await self.bot.wait_for(
                    'message', 
                    check = lambda m: m.author == message.author and m.channel == message.channel, 
                    timeout = limits['max']
                )
                if (latest.created_at - handmember['l']).total_seconds() < limits['min']:
                    continue
                if latest.content.startswith(('l!', 't!', '!', '-')):
                    continue
                else: 
                    handmember['l'] = latest.created_at
                    if len(clean(latest.content)) > 4 and len(self.handled) > 1:
                        score = member.score
                        score += 1 * config.values['xp']['modifer']
                        await member.save()
                        handmember['st'] += 1
                        if score in levels:
                            await message.channel.send(
                                embed = discord.Embed(
                                    title = f'🎉 {random.choice(["Конгратс!", "Поздравляем!"])}',
                                    description = f'{latest.author.mention} получил(а) {levels[score]}-й уровень, набрав {inflect_by_amount(score, "очко")}',
                                    color = 0xffc83d
                                )
                            )

        except asyncio.TimeoutError:
            self.handled.pop(message.author.id)

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
        member = await MemberDB(target.id).fetch()
        xp = member.score
        current_level = get_level(xp)

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
            value = f'```diff\n+ {inflect_by_amount(get_level(xp, next_needed = True)-xp, "очко")}\n```'
        ).add_field(
            name = 'Прогресс',
            value = f'```{bh.bar()}| {current_level+1}lvl ({bh.persent}%)```',
            inline = False
        )
        if ctx.author.id in self.handled:
            handmember = self.handled[ctx.author.id]
            embed.set_footer(text = f'l: {handmember["l"].time()}; ts: {handmember["st"]}')
        await ctx.send(
            embed = embed
        )
    
    @_score.command(name = 'top')
    async def _top(self, ctx):
        menu = ScoringPages(Scoring.query)
        await menu.start(ctx)

    @tasks.loop()
    async def giveaway(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, messsage):
        pass

def setup(bot):
    bot.add_cog(ScoringSystem(bot))
