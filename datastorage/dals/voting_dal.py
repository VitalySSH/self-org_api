from typing import List, cast

from sqlalchemy import select, func, distinct

from datastorage.dals.base import DAL
from datastorage.database.models import CommunitySettings
from datastorage.interfaces import VotingParams, PercentByName


class VotingDAL(DAL):

    async def calculate_voting_params(self, community_id) -> VotingParams:
        query = select(func.avg(CommunitySettings.vote), func.avg(CommunitySettings.quorum))
        query.filter(CommunitySettings.community == community_id)
        rows = await self._session.execute(query)
        vote, quorum = rows.first()

        return VotingParams(vote=int(vote), quorum=int(quorum))

    async def get_all_community_names(self, community_id) -> List[str]:
        query = select(CommunitySettings.name).distinct()
        query.filter(CommunitySettings.community == community_id)
        query.group_by(CommunitySettings.name)
        rows = await self._session.execute(query)

        return cast(List[str], rows.scalars().all())

    async def get_voting_data_by_names(self, community_id) -> List[PercentByName]:
        query = select(func.count()).select_from(CommunitySettings)
        query.filter(CommunitySettings.community == community_id)
        all_rows = await self._session.execute(query)
        total_count = all_rows.scalars().first()
        query = (
            select(CommunitySettings.name, func.count(CommunitySettings.name).label('count'))
            .filter(CommunitySettings.community == community_id)
            .group_by(CommunitySettings.name)
        )
        rows = await self._session.execute(query)

        return [PercentByName(name=row[0], percent=int((row[1]/total_count) * 100))
                for row in rows.all()]
