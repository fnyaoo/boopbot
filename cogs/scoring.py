import re
import random
import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from utils import (
    inflect_by_amount,
    levels,
    levels_inverted,
    get_level,
    get_next,
    BarCreator,
    goodnight_messages
)
from utils.db import Members, ScoreDailyLog, F
from utils.menus import ScoringPages
from checks import is_admin


class ScoringSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        bot.in_active = {}

        self._qualified_name = 'Активность в чате'
        self.description = 'Скоринг-система и команды взаимодействия с ней.'
    
    @staticmethod
    async def dayend_embed(sum: int, count: int, top):
        emojis = ['🏆 1', '🎖 2', '🏅 3']
        embed = discord.Embed(
            title = '🌃 ' + random.choice(goodnight_messages),
            description = (f'В общей сумме сегодня было заработано {inflect_by_amount(sum, "очко")}\n'
                           f'В чате общалось {inflect_by_amount(count, "человек")}'),
            color = 0x226699
        )
        for i, val in enumerate(emojis):
            try:
                embed.add_field(
                    name = f'{val} место',
                    value = f'<@{(await top[i].member).discord_id}> — {inflect_by_amount(top[i].score, "очко")}',
                    inline = False
                )
            except KeyError as e:
                print(repr(e))
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        self.scorelog_schedule.start()


    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if (message.content.startswith(('l!', 't!', '!', '-')) or 
            author.bot or 
            author.id in self.bot.in_active or 
            (not message.channel.id in [824997091725017090])):
            return
        self.bot.in_active[author.id] = {'last': message.created_at}

        def clean(content: str):
            new_ct = re.sub('<(?:@|#|:\S+:|@&)\d{18}>', '', content)
            new_ct = re.sub('[^a-zA-Zа-яА-ЯёЁ]', '', new_ct)
            return new_ct

        # new method
        handmember = self.bot.in_active[author.id]

        try:
            while True:
                latest = await self.bot.wait_for(
                    'message', 
                    check = lambda m: m.author == author and m.channel == message.channel, 
                    timeout = 80
                )

                if (latest.created_at - handmember['last']).total_seconds() < 40:
                    continue
                if latest.content.startswith(('l!', 't!', '!', '-')):
                    continue

                handmember['last'] = latest.created_at

                if len(clean(latest.content)) > 4 and len(self.bot.in_active) > 1:
                    member, _ = await Members.get_or_create(discord_id = str(author.id))
                    await ScoreDailyLog.get_or_create(member = member)

                    await ScoreDailyLog.filter(member = member).update(score = F('score') + 1)
                    await Members.filter(discord_id = member.discord_id).update(score = F('score') + 1)

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
            self.bot.in_active.pop(author.id)

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

        member, _ = await Members.get_or_create(discord_id = str(target.id))
        log = await ScoreDailyLog.get_or_none(member = member)
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
        )
        if log is not None:
            embed.add_field(
                name = 'За сегодня',
                value = f'```asciidoc\n= {inflect_by_amount(log.score, "очко")}\n```',
                inline = False
            )
        embed.add_field(
            name = 'Прогресс',
            value = f'```{bh.bar()}| {current_level+1}lvl ({bh.persent}%)```',
            inline = False
        )

        if ctx.author.id in self.bot.in_active:
            handmember = self.bot.in_active[ctx.author.id]
            embed.set_footer(text = f'last: {handmember["last"].time()}')
        await ctx.send(embed = embed)

    @_score.command(name = 'top')
    async def _top(self, ctx):
        query = (Members
            .exclude(score = 0)
            .order_by('-score')
        )
        menu = ScoringPages(await query)
        await menu.start(ctx)
    
    @_score.command(name = 'dailytop')
    async def _dailytop(self, ctx):
        query = (ScoreDailyLog
            .exclude(score = 0)
            .order_by('-score')
            .prefetch_related('member')
        )
        menu = ScoringPages(await query, is_daily = True)
        await menu.start(ctx)
    
    @_score.command(name = 'end_day')
    @is_admin()
    async def dayend_message(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        all_rows = await (ScoreDailyLog
            .all()
            .order_by('-score')
        )
        score_sum = sum(row.score for row in all_rows)
        top = all_rows[:3]

        msg: discord.Message = await channel.send(
            ''.join([f'<@{(await score.member).discord_id}>' for score in top])
        )
        embed = await self.dayend_embed(score_sum, len(all_rows), top)
        await msg.edit(content = '', embed = embed)

    @tasks.loop(hours=24)
    async def scorelog_schedule(self):
        all_rows = await (ScoreDailyLog
            .all()
            .order_by('-score')
        )
        score_sum = sum(row.score for row in all_rows)
        top = all_rows[:3]

        msg: discord.Message = await self.bot.get_channel(824997091725017090).send(
            ''.join([f'<@{(await score.member).discord_id}>' for score in top])
        )
        embed = await self.dayend_embed(score_sum, len(all_rows), top)
        await msg.edit(content = '', embed = embed)
        await ScoreDailyLog.all().delete()

    @scorelog_schedule.before_loop
    async def scheduler(self):
        hour, minute = 23, 59

        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)

        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)

        delta = (future - now)
        print(f'sleeping {delta}')

        await asyncio.sleep(delta.seconds)
    

def setup(bot):
    bot.add_cog(ScoringSystem(bot))
