from enum import Enum
import os
import re
import json
import datetime
import pymorphy2
import random
from PIL import Image

from difflib import SequenceMatcher

from discord.ext import commands


class CustomEmoji:
    @property
    def void(self):
        return '<:void:827958334547951657>'

    def mafia_change(sign: bool):
        """ 
        True — +\n
        False — -
        """
        if sign: return '<:murder_plus:827992228378312704>'
        else:    return '<:murder_minus:827992228491427900>'

    def mafia(sign):
        """
        keys: mafia, doctor, policeman, murder, butterfly, peace
        """
        if   sign == 'mafia':     return '<:mafia:828291470808973393>'
        elif sign == 'doctor':    return '<:doctor:828294664998092831>'
        elif sign == 'murder':    return '<:murder:828298357771337738>'
        elif sign == 'butterfly': return '<:butterfly:828296595396755496>'
        elif sign == 'peace':     return '<:peace:828299018459021313>'
        elif sign == 'policeman': return '<:policeman:828298447755935795>'
        else: return [
            '<:mafia:828291470808973393>', 
            '<:murder:828298357771337738>', 
            '<:policeman:828298447755935795>',
            '<:doctor:828294664998092831>',
            '<:butterfly:828296595396755496>',
        ]


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

emoji_pattern = re.compile(u"["
u"\U0001F600-\U0001F64F"  # emoticons
u"\U0001F300-\U0001F5FF"  # symbols & pictographs
u"\U0001F680-\U0001F6FF"  # transport & map symbols
u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "]", flags= re.UNICODE)

layout = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                           'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'
                           "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                           'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'),
                           "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                           'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'
                           "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                           'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'))


morph = pymorphy2.MorphAnalyzer()

def inflect_by_amount(amount, word):
    parse = morph.parse(word)[0]
    inflect = parse.word

    _number = int(str(amount)[-2:])
    if _number > 10 and _number < 15:
        inflect = parse.inflect({'plur', 'gent'}).word
    else:
        _number = int(str(_number)[-1:])
        if _number == 0:
            inflect = parse.inflect({'plur', 'gent'}).word
        elif _number == 1:
            inflect = word
        elif _number > 4:
            inflect = parse.inflect({'plur', 'gent'}).word
        elif _number > 1:
            inflect = parse.inflect({'gent'}).word
    return f'{amount} {inflect}'

levels = { 0: 0,
    10: 1, 20: 2, 30: 3,
    45: 4, 60: 5, 80: 6,
    100: 7, 120: 8, 150: 9,
    180: 10, 210: 11, 250: 12,
    300: 13, 360: 14, 420: 15,
    500: 16, 580: 17, 650: 18,
    750: 19, 875: 20, 1000: 21,
    1150: 22, 1300: 23, 1500: 24,
    1650: 25, 1900: 26, 2200: 27,
    2500: 28, 2850: 29, 3250: 30
}

levels_inverted = { 0: 0,
    1: 10, 2: 20, 3: 30, 
    4: 45, 5: 60, 6: 80, 
    7: 100, 8: 120, 9: 150, 
    10: 180, 11: 210, 12: 250, 
    13: 300, 14: 360, 15: 420, 
    16: 500, 17: 580, 18: 650, 
    19: 750, 20: 875, 21: 1000, 
    22: 1150, 23: 1300, 24: 1500, 
    25: 1650, 26: 1900, 27: 2200, 
    28: 2500, 29: 2850, 30: 3250
}

def get_level(xp: int, next_needed: bool = False) -> int:
    for amount in levels:
        if amount < xp: continue
        else:
            if next_needed:
                values = list(levels.values())
                keys = list(levels.keys())
                
                return keys[values.index(levels[amount])]
            else:
                return levels[amount]-1
    if next_needed:
        return 0
    else:
        return levels[3250]


class BarCreator:
    def __init__(self, min, max, current):
        self.min = min
        self.max = max
        self.current = current

    @property
    def raw_persent(self):
        return (self.current - self.min) / (self.max - self.min)
    @property
    def persent(self):
        return int(round(self.raw_persent, 2) * 100)

    def bar(self, bar_length = 25, chars = ['█', ' ']):
        if self.max == self.min:
            return chars[0] * bar_length
        fill_length = int(self.raw_persent * bar_length)

        return chars[0] * fill_length + chars[1] * (bar_length - fill_length)


class _Config:
    def __init__(self):
        self.now = datetime.datetime.now
        self.filepath = 'config.json'

        self.last_fetch = self.now()
        self._update_after = 300
        self.fetch()
    
    def __getitem__(self, key):
        return self.values[key] 
    
    def fetch(self):
        with open(self.filepath, 'r') as f:
            self._cached_values = json.load(f)
        self.last_fetch = self.now()
        return self._cached_values
    
    @property
    def values(self):
        if (self.last_fetch - self.now()).total_seconds() > self._update_after:
            return self.fetch()
        return self._cached_values

    @values.setter
    def values(self, value):
        def foo(subdirectory: dict, val):
            for key in val:
                if isinstance(val[key], dict):
                    foo(subdirectory[key], val[key])
                else:
                    subdirectory[key] = val[key]
                
        foo(self._cached_values, value)
        with open(self.filepath, 'w') as f:
            json.dump(self._cached_values, f, indent=4)
        self.last_fetch = self.now()


config = _Config()

def generate_setup(directory: str):
    def setup(bot: commands.Bot):
        extensions = (name[:-3] for name in os.listdir(directory) if name.endswith('.py') and name not in ('__init__.py'))
        for ext in extensions:
            try:
                bot.load_extension(f'{directory}.{ext}')
            except commands.ExtensionError as e:
                print(f'WARNING: {directory}.{ext} raised {e.name}: {e}')
    return setup

def generate_board():
    return Image.new('RGBA', (500, 500), (0, 0, 0, 0))

def drop_card(card_name: str, previous_image: Image.Image = None, lift: bool = True) -> Image.Image:
    if previous_image is None:
        previous_image = generate_board()
    card = Image.open(f'assets/uno_cards/{card_name}.png')
    
    bg_w, bg_h = previous_image.size
    if lift:
        card = card.rotate(random.randint(-20, 20), Image.BICUBIC, True)
        card_w, card_h = card.size
        offset = ((bg_w - card_w) // 2 + random.randint(-5, 5), (bg_h - card_h) // 2 + random.randint(-5, 5))
    else:
        card_w, card_h = card.size
        offset = ((bg_w - card_w) // 2, (bg_h - card_h) // 2)
    new_image = previous_image.copy()
    new_image.paste(card, offset, card)
    return new_image

class UnoEmojis(Enum):
    YELLOW_ZERO  = '<:yellow_0:864413410406301696>'
    YELLOW_ONE   = '<:yellow_1:864413462746234892>'
    YELLOW_TWO   = '<:yellow_2:864413504537493506>'
    YELLOW_THREE = '<:yellow_3:864413557197897768>'
    YELLOW_FOUR  = '<:yellow_4:864413601833025536>'
    YELLOW_FIVE  = '<:yellow_5:864413643138662401>'
    YELLOW_SIX   = '<:yellow_6:864413701796397066>'
    YELLOW_SEVEN = '<:yellow_7:864413972018364458>'
    YELLOW_EIGHT = '<:yellow_8:864414005573058580>'
    YELLOW_NINE  = '<:yellow_9:864414043904147476>'
    BLUE_ZERO    = '<:blue_0:864414087966621696>'
    BLUE_ONE     = '<:blue_1:864414132513538068>'
    BLUE_TWO     = '<:blue_2:864414162741624832>'
    BLUE_THREE   = '<:blue_3:864414204059320320>'
    BLUE_FOUR    = '<:blue_4:864414251950276679>'
    BLUE_FIVE    = '<:blue_5:864414285878788126>'
    BLUE_SIX     = '<:blue_6:864414322225840158>'
    BLUE_SEVEN   = '<:blue_7:864414356413743135>'
    BLUE_EIGHT   = '<:blue_8:864414399079120916>'
    BLUE_NINE    = '<:blue_9:864414433614626826>'
    GREEN_ZERO   = '<:green_0:864414495668174858>'
    GREEN_ONE    = '<:green_1:864414641119297536>'
    GREEN_TWO    = '<:green_2:864414693879578634>'
    GREEN_THREE  = '<:green_3:864414737093754880>'
    GREEN_FOUR   = '<:green_4:864414772657520651>'
    GREEN_FIVE   = '<:green_5:864414807331307521>'
    GREEN_SIX    = '<:green_6:864415030366568510>'
    GREEN_SEVEN  = '<:green_7:864415070803722310>'
    GREEN_EIGHT  = '<:green_8:864415102773100544>'
    GREEN_NINE   = '<:green_9:864415159313367060>'
    RED_ZERO     = '<:red_0:864415269107138580>'
    RED_ONE      = '<:red_1:864415317258403861>'
    RED_TWO      = '<:red_2:864415346546180096>'
    RED_THREE    = '<:red_3:864415408827400192>'
    RED_FOUR     = '<:red_4:864415438087651340>'
    RED_FIVE     = '<:red_5:864415475298861067>'
    RED_SIX      = '<:red_6:864415545843515403>'
    RED_SEVEN    = '<:red_7:864415577732939796>'
    RED_EIGHT    = '<:red_8:864415607444865034>'
    RED_NINE     = '<:red_9:864415636598554684>'
    YELLOW_SKIP      = '<:yellow_skip:864416693657141278>'
    YELLOW_REVERSE   = '<:yellow_reverse:864416828918202389>'
    YELLOW_DRAW_TWO  = '<:yellow_draw_two:864416911210446858>'
    BLUE_SKIP        = '<:blue_skip:864417157202837534>'
    BLUE_REVERSE     = '<:blue_reverse:864417235173638144>'
    BLUE_DRAW_TWO    = '<:blue_draw_two:864417297107779636>'
    GREEN_SKIP       = '<:green_skip:864417391433613315>'
    GREEN_REVERSE    = '<:green_reverse:864417460274724864>'
    GREEN_DRAW_TWO   = '<:green_draw_two:864417547708661786>'
    RED_SKIP         = '<:red_skip:864417643749703711>'
    RED_REVERSE      = '<:red_reverse:864417714642616340>'
    RED_DRAW_TWO     = '<:red_draw_two:864417770795696148>'
    WILD_COLOR       = '<:wild_color:864417877938667550>'
    WILD_DRAW_FOUR   = '<:wild_draw_four:864417913581600778>'