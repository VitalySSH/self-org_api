from typing import List, cast

from sqlalchemy import select, func, distinct

from datastorage.dals.base import DAL
from datastorage.database.models import CommunitySettings
from datastorage.interfaces import VotingParams


class VotingDAL(DAL):

    async def calculate_voting_params(self, community_id) -> VotingParams:
        query = select(func.avg(CommunitySettings.vote), func.avg(CommunitySettings.quorum))
        query.filter(CommunitySettings.community == community_id)
        rows = await self._session.execute(query)
        vote, quorum = rows.first()
        return VotingParams(vote=int(vote), quorum=int(quorum))

    async def get_all_community_names(self, community_id) -> List[str]:
        query = select(distinct(cast("ColumnElement[_T]", CommunitySettings.name)))
        query.filter(CommunitySettings.community == community_id)
        query.group_by(CommunitySettings.name).distinct()
        rows = await self._session.execute(query)
        return cast(List[str], rows.scalars().all())
