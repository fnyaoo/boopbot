from tortoise.models import Model
from tortoise.fields import CharField, JSONField, IntField


class Members(Model):
    discord_id = CharField(18, pk = True)
    score      = IntField(default = 0)

    class Meta:
        table = 'members'

class MemberDB:
    def __init__(self, member_id) -> None:
        self.member_id = str(member_id)
    
    async def fetch(self) -> Members:
        return Members.get_or_create(discord_id = self.member_id)[0]

class __Scoring:
    def __init__(self) -> None:
        self._query = (Members
            .exclude(score = 0)
            .order_by('-score')
        )
    
    @property
    async def query(self):
        return await self._query

Scoring = __Scoring()