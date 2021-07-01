import discord
from discord.ext import commands

from errors import BadgeBadArgument
from checks import is_admin
from utils import config, 
from utils.database import BadgesManage, MembersDB, Badge_Products


class Badges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.badges_client = BadgesManage()

        self._qualified_name = 'Бейджи'
        self.description = 'Команды, связанные с бейджами'


    async def send_cats(self, old_msg):
        rows = self.badges_client.fetch_categories()
        embed = discord.Embed(
            title = '📔 Бэйджи',
            color = 0xd99e82
        )
        for itr_category in rows:
            embed.add_field(
                name = itr_category['name'],
                value = itr_category['description'],
                inline = False
            )
        await old_msg.edit(embed=embed)

    async def send_badges_by_cats(self, old_msg, cat):
        embed = discord.Embed(
            title = f"📔 {cat['name']}",
            description = cat['description'],
            color = 0xd99e82
        )
        for itr_badge in self.badges_client.fetch_badges(cat['row']):
            embed.add_field(
                name = f'{itr_badge["char"]} {itr_badge["name"]}',
                value = itr_badge['description'],
                inline = False
            )
        await old_msg.edit(embed=embed)


    @commands.group(name='badge', aliases=['badges'], invoke_without_command = True)
    async def badges_group(self, ctx: commands.Context, *, imput = None):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send(embed=discord.Embed(description='Подождите...'))
            if imput:
                imput = imput.lower().capitalize()
                try:
                    cat = self.badges_client.fetch_category(imput)
                    await self.send_badges_by_cats(msg, cat)
                
                except BadgeBadArgument:
                    try:
                        badge = self.badges_client.fetch_badge(imput)

                        embed = discord.Embed(
                            title = f'{badge["char"]} {badge["name"]}',
                            description = badge['description']
                        )
                        await msg.edit(embed=embed)
                        await msg.add_reaction('✅')

                        def check(r, u):
                            return str(r.emoji) == '✅' and u == ctx.author
                        r = await self.bot.wait_for('reaction_add', check=check, timeout=60)
                        await msg.edit(content = 'Подождите...')
                        
                        badge_id = badge['row'].id

                        if badge_id in (int(i) for i in config['special_badges']):
                            if not ctx.author.id in config['special_badges'][str(badge_id)]:
                                return await msg.edit(content = 'У вас нет доступа к этому бейджу')

                        modal = MembersDB(ctx.author.id)
                        badges_json = modal.member.json['badges']
                        old_json = badges_json.copy()

                        badges_json['equiped'] = badge_id
                        badges_json['uses'][str(badge_id)] = badges_json['uses'].setdefault(badge_id, 0) + 1
                        modal.save()
                        old_badge = Badge_Products.get_by_id(old_json['equiped'])

                        if old_json['equiped']:
                            await ctx.author.edit(nick = f'{ctx.author.display_name.strip(("・"+old_badge.char))}・{badge["char"]}')
                        else:
                            await ctx.author.edit(nick = f'{ctx.author.display_name}・{badge["char"]}')
                        await msg.edit(content = f'Вы надели бейдж "{badge["name"]}"')
                    except BadgeBadArgument:
                        return await msg.edit(content = f'Не найдена категория или бейдж с именем {imput}.')
                    except TimeoutError:
                        return await msg.edit(embed=embed.set_footer('Достигнут лимит времени'))
            
            else:
                await self.send_cats(msg)

    @badges_group.group(name='create', invoke_without_command = True)
    @is_admin()
    async def create_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Вы можете создать бейдж или категорию')

    @create_group.command(name='category')
    async def category_create(self, ctx: commands.Context, name, desc):
        msg = await ctx.send(
            embed=discord.Embed(
                title = 'Подтвердите создание',
            ).add_field(
                name = 'Название',
                value = name
            ).add_field(
                name = 'Описание',
                value = desc
            )
        )
        rs = ['✅', '❌']
        def check(r, u):
            return str(r.emoji) in rs and u == ctx.author
        
        for r in rs: await msg.add_reaction(r)
        react, user = await self.bot.wait_for('reaction_add', check=check)
        await msg.delete()

        if str(react.emoji) == rs[0]:
            row = BadgesManage().create_category(name, desc)
            await ctx.send(
                embed=discord.Embed(
                    title='Добавлена категория',
                    description=f'Название: `{row.name}`\nОписание: `{row.description}`'
                )
            )
        else:
            await ctx.send('Добавление отменено')

    @create_group.command(name='badge')
    async def badge_create(self, ctx: commands.Context, char, name, desc, cat_name):
        cat = self.badges_client.fetch_category(cat_name)
        msg = await ctx.send(
            embed=discord.Embed(
                title = 'Подтвердите создание',
            ).add_field(
                name = 'Бейдж',
                value = char
            ).add_field(
                name = 'Название',
                value = name
            ).add_field(
                name = 'Описание',
                value = desc
            ).add_field(
                name = 'Категория',
                value = cat['name']
            )
        )
        rs = ['✅', '❌']
        def check(r, u):
            return str(r.emoji) in rs and u == ctx.author
        
        for r in rs: await msg.add_reaction(r)
        react, user = await self.bot.wait_for('reaction_add', check=check)
        await msg.delete()

        if str(react.emoji) == rs[0]:
            row = self.badges_client.create_badge(char, name, desc, cat['row'])

            
            await ctx.send(
                embed=discord.Embed(
                    title='Добавлен бейдж',
                    description=f'Чар: `{row.char}`\n' \
                                f'Название: `{row.name}`\n' \
                                f'Описание: `{row.description}`\n' \
                                f'Категория: `{row.category.name}`'
                )
            )
        else:
            await ctx.send('Добавление отменено')

    @badges_group.command(name='unequip')
    async def unequip_badge(self, ctx: commands.Context):
        modal = MembersDB(ctx.author.id)
        badges_json = modal.member.json['badges']
        if not badges_json['equiped'] is None:
            badge = Badge_Products.get_by_id(badges_json['equiped'])
            await ctx.author.edit(nick = ctx.author.display_name.strip(f'・{badge.char}'))

            badges_json['equiped'] = None
            modal.save()

        await ctx.send('Теперь вы не носите бейдж.')


def setup(bot):
    bot.add_cog(Badges(bot))
