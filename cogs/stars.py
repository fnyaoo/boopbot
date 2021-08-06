import re
import asyncio

import discord
from discord.ext import commands
from tortoise.exceptions import IntegrityError

from utils.db import StarEntries, Members
# just copy-pasted whole code from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/stars.py
# and adapted for my db
class StarError(Exception): ...

class Starboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.spoilers = re.compile(r'\|\|(.+?)\|\|')
        self._message_cache = {}
        self._about_to_be_deleted = set()
        self._lock = asyncio.Lock(loop=self.bot.loop)

    @commands.Cog.listener()
    async def on_ready(self):
        self.starboard: discord.TextChannel = self.bot.get_channel(865617516269142026)

    def star_emoji(self, stars):
        if 5 > stars >= 0:
            return '\N{WHITE MEDIUM STAR}'
        elif 10 > stars >= 5:
            return '\N{GLOWING STAR}'
        elif 25 > stars >= 10:
            return '\N{DIZZY SYMBOL}'
        else:
            return '\N{SPARKLES}'

    def star_gradient_color(self, stars):
        p = stars / 13
        if p > 1.0:
            p = 1.0

        red = 255
        green = int((194 * p) + (253 * (1 - p)))
        blue = int((12 * p) + (247 * (1 - p)))
        return (red << 16) + (green << 8) + blue

    def is_url_spoiler(self, text, url):
        spoilers = self.spoilers.findall(text)
        for spoiler in spoilers:
            if url in spoiler:
                return True
        return False

    def get_emoji_message(self, message, stars):
        emoji = self.star_emoji(stars)

        if stars > 1:
            content = f'{emoji} **{stars}** {message.channel.mention} ID: {message.id}'
        else:
            content = f'{emoji} {message.channel.mention} ID: {message.id}'

        embed = discord.Embed(description=message.content)
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image' and not self.is_url_spoiler(message.content, data.url):
                embed.set_image(url=data.url)
        if message.attachments:
            file = message.attachments[0]
            spoiler = file.is_spoiler()
            if not spoiler and file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
                embed.set_image(url=file.url)
            elif spoiler:
                embed.add_field(name='Вложение', value=f'||[{file.filename}]({file.url})||', inline=False)
            else:
                embed.add_field(name='Вложение', value=f'[{file.filename}]({file.url})', inline=False)

        ref = message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            embed.add_field(name='Ответ на...', value=f'[{ref.resolved.author}]({ref.resolved.jump_url})', inline=False)

        embed.add_field(name='Оригинал', value=f'[Прыг]({message.jump_url})', inline=False)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        embed.timestamp = message.created_at
        embed.colour = self.star_gradient_color(stars)
        return content, embed

    async def get_message(self, channel, message_id) -> discord.Message:
        try:
            return self._message_cache[message_id]
        except KeyError:
            try:
                o = discord.Object(id=message_id + 1)
                msg = await channel.history(limit=1, before=o).next()

                if msg.id != message_id:
                    return None

                self._message_cache[message_id] = msg
                return msg
            except Exception:
                return None

    async def reaction_action(self, fmt, payload):
        if str(payload.emoji) != '⭐':
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel_or_thread(payload.channel_id)
        if not isinstance(channel, (discord.Thread, discord.TextChannel)):
            return

        method = getattr(self, f'{fmt}_message')

        user = payload.member or (await guild.fetch_member(payload.user_id))
        if user is None or user.bot:
            return

        await method(channel, payload.message_id, payload.user_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_action('star', payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.reaction_action('unstar', payload)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.message_id in self._about_to_be_deleted:
            self._about_to_be_deleted.discard(payload.message_id)
            return
        if self.starboard.id != payload.channel_id:
            return

        await (StarEntries
            .filter(bot_message_id = str(payload.message_id))
            .delete()
        )

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        if payload.message_ids <= self._about_to_be_deleted:
            self._about_to_be_deleted.difference_update(payload.message_ids)
            return
        if self.starboard.id != payload.channel_id:
            return

        await (StarEntries
            .filter(bot_message_id__in = [str(id) for id in payload.message_ids])
            .delete()
        )

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel_or_thread(payload.channel_id)
        if channel is None or not isinstance(channel, (discord.Thread, discord.TextChannel)):
            return

        star = (await StarEntries.filter(message_id = str(payload.message_id)))[0]
        await star.delete()

        msg = await self.get_message(self.starboard, int(star.bot_message_id))
        if msg is not None:
            await msg.delete()

    async def star_message(self, channel, message_id, starrer_id):
        async with self._lock:
            await self._star_message(channel, message_id, starrer_id)

    async def _star_message(self, channel, message_id, starrer_id):
        if channel.id == self.starboard.id:
            record = await (StarEntries
                .filter(bot_message_id = message_id)
            )
            record = record[0]

            ch = channel.guild.get_channel_or_thread(int(record.channel_id))
            if ch is None:
                raise StarError('Не удалось найти первоначальный канал.')

            return await self.star_message(ch, record.message_id, starrer_id)
        msg = await self.get_message(channel, message_id)

        if msg is None:
            raise StarError('Не удалось найти сообщение.')

        if msg.author.id == starrer_id:
            raise StarError('Вы не можете поставить звезду на свое сообщение.')

        empty_message = len(msg.content) == 0 and len(msg.attachments) == 0
        if empty_message or msg.type not in (discord.MessageType.default, discord.MessageType.reply):
            raise StarError('На это сообщение нельзя поставить звезду.')

        ids = {
            'message_id': str(message_id),
            'channel_id': str(channel.id),
            'author_id': str(msg.author.id)
        }
        try:
            entry = await StarEntries.create(**ids)
        except IntegrityError:
            entry = await StarEntries.get(message_id = ids['message_id'])
        await entry.starrers.add((await Members.get_or_create(discord_id = str(starrer_id)))[0])

        count = await entry.starrers.all().count()
        if count < 2:
            return

        # at this point, we either edit the message or we create a message
        # with our star info
        content, embed = self.get_emoji_message(msg, count)

        # get the message ID to edit:
        bot_message_id = entry.bot_message_id

        if bot_message_id is None:
            new_msg = await self.starboard.send(content, embed=embed)
            entry.bot_message_id = new_msg.id
            await entry.save()
        else:
            new_msg = await self.get_message(self.starboard, bot_message_id)
            if new_msg is None:
                # deleted? might as well purge the data
                await (StarEntries
                    .filter(message_id = message_id)
                    .delete()
                )
            else:
                await new_msg.edit(content=content, embed=embed)

    async def unstar_message(self, channel, message_id, starrer_id):
        async with self._lock:
            await self._unstar_message(channel, message_id, starrer_id)

    async def _unstar_message(self, channel, message_id, starrer_id):
        if channel.id == self.starboard.id:
            record = await (StarEntries
                .filter(bot_message_id = message_id)
            )
            if len(record) == 0:
                raise StarError('Не удалось найти сообщение.')
            record = record[0]

            ch = channel.guild.get_channel_or_thread(record.channel_id)
            if ch is None:
                raise StarError('Не удалось найти первоначальный канал.')

            return await self.unstar_message(ch, record.message_id, starrer_id)
        record = await StarEntries.get_or_none(message_id = message_id)
        if record is None:
            raise StarError('\N{NO ENTRY SIGN} Этого сообщения ещё нет на доске.')
        await record.fetch_related('starrers')
        starrer = await Members.get_or_create(discord_id = starrer_id)
        if starrer not in record.starrers:
            raise StarError('\N{NO ENTRY SIGN} Вы ещё на поставили звезду на это сообщение.')

        bot_message_id = record.bot_message_id

        count = await (record.starrers
            .all()
            .count()
        )

        if count == 0:
            # delete the entry if we have no more stars
            await record.delete()

        if bot_message_id is None:
            return

        bot_message = await self.get_message(self.starboard, bot_message_id)
        if bot_message is None:
            return

        if count < 2:
            self._about_to_be_deleted.add(bot_message_id)
            if count:
                # update the bot_message_id to be NULL in the table since we're deleting it
                record.bot_message_id = None
                await record.save()

            await bot_message.delete()
        else:
            msg = await self.get_message(channel, message_id)
            if msg is None:
                raise StarError('\N{BLACK QUESTION MARK ORNAMENT} Это сообщение не найдено.')

            content, embed = self.get_emoji_message(msg, count)
            await bot_message.edit(content=content, embed=embed)

def setup(bot):
    bot.add_cog(Starboard(bot))