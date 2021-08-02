from tortoise.fields.relational import ForeignKeyRelation
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    IntField,
    ForeignKeyField,
    ForeignKeyRelation,
    ReverseRelation
)


__all__ = (
    'Members',
    'ScoreDailyLog'
)

class Members(Model):
    discord_id = CharField(18, pk = True)
    score      = IntField(default = 0)
    score_log: ReverseRelation['ScoreDailyLog']

    def __str__(self) -> str:
        discord_id = self.discord_id
        return f'Member({discord_id=})'

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