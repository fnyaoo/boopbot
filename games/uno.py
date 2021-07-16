from enum import Enum
from io import BytesIO
from itertools import groupby
from typing import List, Optional, Tuple
from utils import UnoEmojis, drop_card
import discord
from discord.ext import commands
import random
from itertools import cycle


class Color(Enum):
    BLUE     = (0, 'Синяя')
    GREEN    = (1, 'Зелёная')
    RED      = (2, 'Красная')
    YELLOW   = (3, 'Жёлтая')
class Digit(Enum):
    ZERO     = (0, '0', '')
    ONE      = (1, '1', '')
    TWO      = (2, '2', '')
    THREE    = (3, '3', '')
    FOUR     = (4, '4', '')
    FIVE     = (5, '5', '')
    SIX      = (6, '6', '')
    SEVEN    = (7, '7', '')
    EIGHT    = (8, '8', '')
    NINE     = (9,   '9', '')
    REVERSE  = (10,  '"Реверс"',      'Направление хода меняется на противоположное')
    SKIP     = (11,  '"Скип"',        'Следующий игрок пропускает ход')
    DRAW_TWO = (12,  '"Возьми две"',  'Следующий игрок получает 2 карты')
class Wild(Enum):
    COLOR     = (13, 'Выбор цвета',   'Вы можете выбрать текущий цвет')
    DRAW_FOUR = (14, 'Возьми четыре', 'Следующий берет 4 карты и вы выбираете цвет')


class Card:
    __cards__: Optional[List['Card']] = None

    def __init__(self, color: Color = None, digit: Digit = None, wild: Wild = None):
        self.color = color
        self.spec = wild or digit or None
        if self.spec is None:
            raise TypeError('ты даун')
    
    @property
    def label(self) -> str:
        if isinstance(self.spec, Wild):
            return self.spec.value[1]
        return f'{self.color.value[1]} {self.spec.value[1]}'
    def __str__(self) -> str:
        return f'{self.emoji} {self.label}'
    def __repr__(self) -> str:
        if not isinstance(self.spec, Wild):
            return f'{self.color.name}_{self.spec.name}'
        return f'WILD_{self.spec.name}'

    @property
    def description(self) -> str:
        return self.spec.value[2]
    
    @property
    def emoji(self):
        return UnoEmojis.__members__[repr(self)].value
    
    def __format__(self, format_spec: str) -> str:
        if format_spec == 'label':
            return self.label
        if format_spec == 'description':
            return self.description
        if format_spec == 'emoji':
            return self.emoji
        return ''
    
    @classmethod
    def get_all_cards(cls):
        if cls.__cards__ is None:
            r = []
            for color in Color.__members__.values():
                temp = []
                for digit in Digit.__members__.values():
                    temp.append(Card(color, digit))
                r += temp
            for wild in Wild.__members__.values():
                r += [Card(wild=wild)]*2
            cls.__cards__ = r
        return cls.__cards__

    def is_playable(self, top_card: 'Card'):
        if isinstance(self.spec, Wild):
            return True
        return any([self.spec.value[0] == top_card.spec.value[0], self.color.value[0] == top_card.color.value[0]])
    
    def is_unstopable(self, top_card: 'Card'):
        if isinstance(self.spec, Wild):
            return self.spec.value[0] == top_card.spec.value[0]
        return all([self.spec.value[0] == top_card.spec.value[0], self.color.value[0] == top_card.color.value[0]])

class ThrowSelect(discord.ui.Select):
    def __init__(self, cards: List[Card]) -> None:
        super().__init__(placeholder='Выберите карту')

        for i, card in enumerate(cards):
            self.add_option(
                label = format(card, 'label'),
                description = format(card, 'description'),
                emoji = format(card, 'emoji'),
                value = i
            )
    
    async def callback(self, interaction: discord.Interaction):
        assert isinstance(self.view, discord.ui.View)
        value = int(self.values[0])
        self.view.interaction = interaction
        self.view.value = value
        self.view.stop()

class UnoView(discord.ui.View):
    def __init__(self, players: List[discord.Member], start_with: int):
        super().__init__(timeout=None)
        self._start_with = start_with
        self._members = players
        self.message: discord.Message = None
        random.shuffle(self._members)

        self.deck = Card.get_all_cards()
        random.shuffle(self.deck)
        self.deck_top = self.deck.pop()
        a = []
        while self.deck_top.spec.value[0] > 9:
            a.append(self.deck_top)
            self.deck_top = self.deck.pop()
        self.deck += a
        print(self.deck_top)

        self.board_image = drop_card(repr(self.deck_top))
        self.playcycle = cycle(self._members)
        
        self.players = {
            player: [self.deck.pop() for i in range(start_with)]
            for player in self._members
        }
        self.current: discord.Member = next(self.playcycle)

    def file_embed(self, addiction: str = None):
        buffer = BytesIO()
        self.board_image.save(buffer, 'png')
        f = discord.File(buffer, "board.png")
        buffer.seek(0)
        embed = discord.Embed(
            title = 'Uno',
            description=f'Сейчас ходит {self.current.mention}. {addiction or ""}'
        ).set_image(url="attachment://board.png")
        return (f, embed)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.message is None:
            self.message = interaction.message
        if interaction.user not in self.players:
            return await interaction.response.send_message('Вы не участник игры.', ephemeral=True)
        return True

    @discord.ui.button(
        label='Показать карты',
        style=discord.ButtonStyle.green
    )
    async def throw_cards(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        throw_view = discord.ui.View(timeout=None)

        cards = self.players[interaction.user]
        sorted_cards = []
        def grouping(c: Card):
            if c.color is not None:
                return c.color.value[0]
            return 4

        for _, group in groupby(sorted(cards, key = grouping), grouping):
            sorted_cards += sorted(group, key = lambda c: c.spec.value[0])
        cards = sorted_cards

        throw_view.add_item(ThrowSelect(cards))
        await interaction.response.send_message('Ваши карты', view=throw_view, ephemeral=True)
        if not await throw_view.wait():
            await self.resolve(interaction.user, cards[throw_view.value])
    
    async def resolve(self, member: discord.Member, card: Card) -> None:
        cards = self.players[member]
        card = cards.pop(cards.index(card))
        print(card)
        if card.is_unstopable(self.deck_top):
            while (a := next(self.playcycle)) != member: pass
            self.current = a
            self.board_image = drop_card(repr(card), self.board_image)
            f, e = self.file_embed(f'{member.mention} положил карту вне очереди')
        elif self.current == member:
            if card.is_playable(self.deck_top):
                self.current = next(self.playcycle)
                self.board_image = drop_card(repr(card), self.board_image)
                f, e = self.file_embed()
            else:
                return await member.send('Вы не можете сыграть эту карту')
        else:
            return await member.send('Сейчас не ваш черёд')
        await self.message.delete()
        self.message = await self.message.channel.send(embed=e, file=f, view=self)
        self.deck_top = card

class Flags(commands.FlagConverter, prefix = '--', delimiter = ' '):
    players: Tuple[discord.Member] = commands.flag(aliases=['members', 'p'])
    start_with: int = commands.flag(aliases=['start_cards', 'amount', 'cards'], default=7)

class Uno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='uno')
    async def uno_game(self, ctx: commands.Context, *, flags: Flags):
        view = UnoView([ctx.author] + list(flags.players), flags.start_with)
        file, embed = view.file_embed()
        await ctx.send('ку', file=file, embed=embed, view=view)

def setup(bot):
    bot.add_cog(Uno(bot))
