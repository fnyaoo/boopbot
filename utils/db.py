from tortoise.models import Model
from tortoise import fields


initiate_json = {
    'badges': {
        'equipped': None,
        'uses': {}
    }
}

class Members(Model):
    discord_id = fields.CharField(18, pk = True)
    json = fields.JSONField(null = True, default = initiate_json)
    score = fields.IntField(default = 0)

class MemberDB:
    def __init__(self, member_id) -> None:
        self.member_id = str(member_id)
    
    async def fetch(self) -> Members:
        return Members.get_or_create(discord_id = self.member_id)[0]

class _Scoring:
    def __init__(self) -> None:
        self._query = (Members
            .exclude(score = 0)
            .order_by('-score')
        )
    
    @property
    async def query(self):
        return await self._query

Scoring = _Scoring()