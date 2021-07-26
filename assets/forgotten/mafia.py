import discord
from discord.ext import commands
from dislash.interactions import *
from dislash import slash_commands
from config import CustomEmoji as ce
import random as rand

rules = {
    '🚶‍♂️': {
        'name': '🚶‍♂️ Пошаговый',
        'value': 'Режим, где все ходят поочереди: ночь, мафия, доктор, день, голосование',
        'rule': ['day', 'vote', 'night', 'mafia', 'policeman', 'doctor', 'butterfly']
    },
    '🔀': {
        'name': '🔀 НЕпошаговый',
        'value': 'Такой же порядок, как и в пошаговом, но ночью все ходят в разнобой',
        'rule': ['day', 'vote', 'night', 'async']
    }
}


class Mafia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lobby = None
        self.rules = discord.Embed(
            title = 'Выберите режим игры',
        )

        for _rule in rules:
            rule = rules[_rule]
            self.rules.add_field(
                name = rule['name'],
                value = rule['value']
            )

    async def game_start(self, inter: Interaction):
        members = self.lobby['members']
        if len(members) in range(4, 5):
            mafia_count = 1
        elif len(members) in range(6, 8):
            mafia_count = 2
        elif len(members) in range(9, 10):
            mafia_count = 3
        elif len(members) in range(11, 14):
            mafia_count = 4
        else:
            return await inter.reply('Слишком мало или слишком много игрроков (6-14)', ephemeral = True)
        is_butterfly = False
        is_murder = False
        is_doctor = True
        msg = await inter.reply('Подождите...')
        reacts = [ce.mafia_change(True), ce.mafia_change(False), ce.mafia('doctor'), ce.mafia('murder'), ce.mafia('butterfly'), '✅']
        for r in reacts:
            await msg.add_reaction(r)

        def check(r, u):
            return str(r.emoji) in reacts and u.id == inter.author.id

        repeating = True
        while repeating:
            peaceful_count = len(members) - mafia_count - (1 if is_butterfly else 0) - (1 if is_murder else 0) - (1 if is_doctor else 0) - 1
            embed = discord.Embed(
                title = 'Панель настроек',
                description = f'Выберете те роли, которые вы хотите увидеть в игре. Всего игроков {len(members)}'
            ).add_field(
                name = f'{ce.mafia("mafia")}Мафия ({mafia_count})',
                value = 'Чёрная роль. Минимум 1 мафия. Каждую ночь выбирают кого убить, а на утро выбранный уже не просыпается.',
            ).add_field(
                name = f'{ce.mafia("policeman")}Комисар',
                value = 'Красная роль. 1 на игру. Каждую ночь проверяет игрока на принадлежнось к чёрным.'
            ).add_field(
                name = f'{ce.mafia("doctor")}Доктор ({"✅" if is_doctor else "❌"})',
                value = 'Красная роль. 1 на игру. Каждую ночь пытается отгадать, кого спасти от мафии (или маньяка).'
            ).add_field(
                name = f'{ce.mafia("butterfly")}Проститутка ({"✅" if is_butterfly else "❌"})',
                value = 'Красная роль. Каждую ночь выбирает игрока, который весь следующий день не может говорить и за которого нельзя голосовать.'
            ).add_field(
                name = f'{ce.mafia("murder")}Маньяк ({"✅" if is_murder else "❌"})',
                value = 'Чёрная роль. Каждую ночь выбирает одного человека, которого он хочет убить. Но в отличии от мафии, на утро жертве предложится выбор из 2-х карт рубашкой вверх, одна убивает, другая нет. Жертва должна выбрать свой исход.'
            ).add_field(
                name = f'{ce.mafia("peace")}Мирный житель ({peaceful_count})',
                value = 'Красная роль. Обычный мирный житель. Ночью спит.'
            )
            await msg.edit(content = None, embed = embed)
            react, user = await self.bot.wait_for('reaction_add', check = check)
            await react.remove(user)
            emoji = str(react.emoji)
            
            if emoji == ce.mafia_change(True):
                mafia_count + =  1
            elif emoji == ce.mafia_change(False):
                mafia_count - =  1
            elif emoji == ce.mafia("murder"):
                is_murder = not is_murder
                mafia_count + =  -1 if is_murder else 1
            elif emoji == ce.mafia("butterfly"):
                is_butterfly = not is_butterfly
            elif emoji == ce.mafia("doctor"):
                is_doctor = not is_doctor
            elif emoji == '✅':
                if peaceful_count > 0:
                    repeating = False
                else:
                    await msg.edit(content = 'Количество ролей не соответствует количеству участников, настройте роли правильно')
            
            raw_roles = ['policeman']
            for i in range(mafia_count):
                raw_roles.append('mafia')
            if is_doctor: raw_roles.append('doctor')
            if is_butterfly: raw_roles.append('butterfly')
            if is_murder: raw_roles.append('murder')
            for i in range(len(members) - len(raw_roles)):
                raw_roles.append('peace')
            rand.shuffle(raw_roles)

            for m in members:
                self.lobby['members'][m] = raw_roles.pop()
            
            await msg.edit(content = 'Роли распределены. Напишите команду `/mafia lobby:Роль`, чтобы узнать свою роль.')

    async def next_turn(self, inter):
        pass


    @slash_commands.command(
        name = 'mafia',
        description = 'Игра "Мафия"',
        guild_ids = [824997091075555419],
        options = [
            Option(
                name = 'lobby',
                description = 'Действия с лобби',
                type = Type.STRING,
                choices = [
                    OptionChoice('Присоединиться', 'join'),
                    OptionChoice('Статус', 'status'),
                    OptionChoice('Роль', 'role'),
                ]
            ),
            Option(
                name = 'mod',
                description = 'Действия с лобби для модератора',
                type = Type.STRING,
                choices = [
                    OptionChoice('Создать', 'create'),
                    OptionChoice('Следующий ход', 'next_turn'),
                    OptionChoice('Остановить и удалить', 'delete'),
                ]
            ),
            Option(
                name = 'kill',
                description = 'Убить (только для мафии)',
                type = Type.USER
            ),
            Option(
                name = 'heal',
                description = 'Вылечить (только для доктора)',
                type = Type.USER
            )
        ]
    )
    async def mafia(self, inter: Interaction):
        options = inter.data.options
        if len(options) < 1:
            return await inter.reply('Слишком мало аргументов', ephemeral = True)
        if len(options) > 1:
            return await inter.reply('Слишком много аргументов', ephemeral = True)
        
        for option in options:
            if self.lobby != None:
                if option == 'lobby':
                    if options[option].value == 'join':
                        if not self.lobby['is_started']:
                            if not inter.author in self.lobby['members']:
                                self.lobby['members'][inter.author] = None
                                return await inter.reply(f'{inter.author.mention} присоединился')
                            else:
                                return await inter.reply('Вы уже всупили в игру', ephemeral = True)
                        else:
                            return await inter.reply('Игра уже началась', ephemeral = True)

                    elif options[option].value == 'status':
                        members_list = ''
                        for member in self.lobby['members']:
                            members_list + =  ce.void() + member.mention + '\n'
                        
                        embed = discord.Embed(
                            title = 'Статус игры',
                            description = "Игра в процессе" if self.lobby['is_started'] else "Игра ещё не начилась"
                        ).add_field(
                            name = 'Игроки',
                            value = members_list
                        )
                        return await inter.reply(embed = embed)
                
                    elif options[option].value == 'role':
                        if inter.author in self.lobby['members']:
                            if self.lobby['is_started']:
                                return await inter.reply(f'Ваша роль: {self.lobby["members"][inter.author]}', ephemeral = True)
                            else:
                                return await inter.reply('Игра ещё не запущена', ephemeral = True)
                        else:
                            return await inter.reply('Вы вне игры', ephemeral = True)

                elif option == 'mod':
                    if self.lobby['mod'] == inter.author:
                        if options[option].value == 'create':
                            return await inter.reply('Лобби уже запущено', ephemeral = True)

                        elif options[option].value == 'next_turn':
                            self.lobby['turn'] + =  1
                            if not self.lobby['is_started']:
                                self.lobby['is_started'] = True
                                await self.game_start(inter)
                            else:
                                def check():
                                    peace = len(filter(lambda x: x != 'mafia' and x != 'murder', self.lobby['members'].values()))
                                    alls = len(self.lobby['members'])
                                    murders = alls - peace
                                    return peace > murders

                                while check():
                                    await self.next_turn(inter)

                        elif options[option].value == 'delete':
                            self.lobby = None
                            return await inter.reply('Игра остановлена')
                    else:
                        return await inter.reply('У вас нет прав на выполнение команды', ephemeral = True)
                
            else:
                if option == 'mod':
                    if options[option].value == 'create':
                        choice = await inter.reply(embed = self.rules)
                        for e in rules:
                            await choice.add_reaction(e)

                        def check(r, u):
                            return inter.author.id == u.id and str(r.emoji) in rules

                        react, user = await self.bot.wait_for('reaction_add', check = check)
                        self.lobby = {
                            'rule': rules[str(react.emoji)]['rule'],
                            'mod': user,
                            'members': {},
                            'is_started': False,
                            'turn': 0
                        }

                        await choice.clear_reactions()
                        return await choice.edit(content = 'Лобби создано', embed = None)
                    else:
                        return await inter.reply('Лобби ещё не создано', ephemeral = True)

def setup(bot):
    bot.add_cog(Mafia(bot))
