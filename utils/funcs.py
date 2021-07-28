import io
import os
import re
import json
import datetime
import pymorphy2

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
                "]", flags =  re.UNICODE)

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
levels_ranges = {
    1: range(0, 10), 2: range(10, 30), 3: range(30, 45), 
    4: range(45, 60), 5: range(60, 80), 6: range(80, 100),
    7: range(100, 120), 8: range(120, 150), 9: range(150, 180), 
    10: range(180, 210), 11: range(210, 250), 12: range(250, 300), 
    13: range(300, 360), 14: range(360, 420), 15: range(420, 500), 
    16: range(500, 580), 17: range(580, 650), 18: range(650, 750), 
    19: range(750, 875), 20: range(875, 1000), 21: range(1000, 1150), 
    22: range(1150, 1300), 23: range(1300, 1500), 24: range(1500, 1650), 
    25: range(1650, 1900), 26: range(1900, 2200), 27: range(2200, 2500), 
    28: range(2500, 2850), 29: range(2850, 3250), 30: range(3250, 5000)
}

levels_inverted = {
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

def get_level(xp: int) -> int:
    for mark, level in levels_ranges.items():
        if xp in level:
            return mark
    return 31

def get_next(xp: int) -> int:
    for mark, level in levels_ranges.items():
        if xp in level:
            return levels_ranges[mark][-1]+1
    return 0

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
        if self.min in (self.max, self.current):
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
            json.dump(self._cached_values, f, indent = 4)
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