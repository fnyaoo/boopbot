from tortoise.fields.relational import ForeignKeyRelation
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    IntField,
    ForeignKeyField,
    ForeignKeyRelation,
    ReverseRelation,
    ManyToManyField,
    ManyToManyRelation
)


__all__ = (
    'Members',
    'ScoreDailyLog',
    'StarEntries'
)

class Members(Model):
    discord_id = CharField(18, pk = True)
    score = IntField(default = 0)

    score_log: ReverseRelation['ScoreDailyLog']
    stared_messages: ReverseRelation['StarEntries']
    starrer_on: ManyToManyRelation['StarEntries']

    def __str__(self) -> str:
        discord_id = self.discord_id
        return f'Member({discord_id=})'
    __repr__ = __str__

    class Meta:
        table = 'members'


class ScoreDailyLog(Model):
    id = IntField(pk = True)
    member: ForeignKeyRelation[Members] = ForeignKeyField('models.Members', 'score_log')
    score = IntField(default = 0)

    def __str__(self) -> str:
        id = self.id
        score = self.score
        return f'ScoreDailyLog({id=}, {score=})'
    __repr__ = __str__

    class Meta:
        table = 'scorelog'


class StarEntries(Model):
    message_id = CharField(18, pk = True)
    bot_message_id = CharField(18, null = True)
    channel_id = CharField(18)
    author = ForeignKeyField('models.Members', 'stared_messages')
    starrers = ManyToManyField('models.Members', 'givenstars', related_name = 'starrer_on')
    
    def __str__(self) -> str:
        message_id = self.message_id
        bot_message_id = self.bot_message_id
        return f'ScoreDailyLog({message_id=}, {bot_message_id=})'
    __repr__ = __str__

    class Meta:
        table = 'starentry'