from functools import wraps

from errors import BadgeBadArgument

import json
from datetime import datetime as dt
from os import environ

from peewee import *
from playhouse.migrate import *
from playhouse.db_url import connect


if environ['IS_HEROKU'] == '0':
    from dotenv import load_dotenv
    load_dotenv()

conn = connect(environ['DATABASE_URL'])
conn.field_types = {'json': 'text'}


class JSONField(Field):
    field_type = 'json'

    def db_value(self, value):
        return json.dumps(value)
    def python_value(self, value):
        return json.loads(value)
class BaseModel(Model):
    class Meta:
        database = conn

# base member modal
class Members(BaseModel):
    discord_id = CharField(18, primary_key = True)
    json = JSONField(null = True)
    score = IntegerField(default = 0)

# badge hierarchy
class Badge_Category(BaseModel):
    name = CharField(25)
    description = CharField()
class Badge_Products(BaseModel):
    char = CharField(16)
    name = CharField()
    description = CharField()
    category = ForeignKeyField(Badge_Category, on_delete = 'cascade', on_update = 'cascade')


iniciate_json = {
    'badges': {
        'equiped': None,
        'uses': {}
    }
}


def connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if conn.is_closed():
            conn.connect()
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            if not conn.is_closed():
                conn.close()
            raise e
        if not conn.is_closed():
            conn.close()
        return res
    return wrapper

class BadgesManage:
    def __init__(self): pass

    @connection
    def create_category(self, name, description):
        return Badge_Category.create(
            name = name,
            description = description
        )
    
    @connection
    def create_badge(self, char, name, description, category: Badge_Category):
        return Badge_Products.create(
            char = char,
            name = name,
            description = description,
            category = category
        )
    
    @connection
    def fetch_category(self, name):
        rows = (Badge_Category
            .select()
            .where(Badge_Category.name == name)
        )
        if len(rows) == 1:
            row = rows[0]
            return {
                'row': row,
                'name': row.name,
                'description': row.description
            }
        else:
            raise BadgeBadArgument(f'Категория {name} не найдена или строки дублируются')
    
    @connection
    def fetch_categories(self):
        rows = (Badge_Category
            .select()
        )
        r = []
        for row in rows:
            r.append(
                {
                    'row': row,
                    'name': row.name,
                    'description': row.description
                }
            )
        return r
    
    @connection
    def fetch_badge(self, bad_name):
        rows = (Badge_Products
            .select()
            .where(Badge_Products.name == bad_name)
        )
        if len(rows) == 1:
            row = rows[0]
            return {
                'row': row,
                'char': row.char,
                'name': row.name,
                'description': row.description,
                'category': row.category
            }
        else: 
            raise BadgeBadArgument(f'Бейдж {bad_name} не найден или строки дублируются')

    @connection
    def fetch_badges(self, category: Badge_Category):
        rows = (Badge_Products
            .select()
            .where(Badge_Products.category == category)
        )
        r = []
        for row in rows:
            r.append(
                {
                    'row': row,
                    'char': row.char,
                    'name': row.name,
                    'description': row.description,
                    'category': row.category
                }
            )
        return r

class MembersDB:
    @connection
    def __init__(self, member_id):
        try:
            self.member = Members.get_by_id(member_id)
        except Members.DoesNotExist:
            self.member = Members.create(
                discord_id = member_id,
                json       = iniciate_json
            )

    @connection
    def set_name(self, name):
        self.member.name = name
        self.member.save()
    
    @connection
    def save(self):
        self.member.save()
    
    @connection
    def set_json(self, dict):
        self.member.json = dict
        self.member.save()

class _Scoring:
    def __init__(self):
        self._query = (Members
            .select()
            .where(Members.score != 0)
            .order_by(Members.score)
        )
    
    @property
    @connection
    def query(self):
        return list(self._query)[::-1]
    
    @query.setter
    def query(self, value):
        self._query = value

Scoring = _Scoring()