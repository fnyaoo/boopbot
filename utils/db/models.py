from tortoise.models import Model
from tortoise.fields import CharField, IntField


__all__ = (
    'Members',
)

class Members(Model):
    discord_id = CharField(18, pk = True)
    score      = IntField(default = 0)

    class Meta:
        table = 'members'