from typing import List

from sqlalchemy import select, func

from datastorage.dals.base import DAL
from datastorage.database.models import CommunitySettings
from datastorage.interfaces import VotingParams, PercentByName


class VotingDAL(DAL):

    async def calculate_voting_params(self, community_id: str) -> VotingParams:
        query = select(func.avg(CommunitySettings.vote), func.avg(CommunitySettings.quorum))
        query.filter(CommunitySettings.community_id == community_id)
        rows = await self._session.execute(query)
        vote, quorum = rows.first()

        return VotingParams(vote=int(vote), quorum=int(quorum))

    async def get_all_community_names(self, community_id: str) -> List[str]:
        query = select(CommunitySettings.name).distinct()
        query.filter(CommunitySettings.community_id == community_id)
        query.group_by(CommunitySettings.name)
        rows = await self._session.scalars(query)

        return list(rows.unique())

    async def get_voting_data_by_names(self, community_id: str) -> List[PercentByName]:
        query = select(func.count()).select_from(CommunitySettings)
        query.filter(CommunitySettings.community_id == community_id)
        all_rows = await self._session.scalars(query)
        data = list(all_rows)
        total_count = data[0] if data else 0
        query = (
            select(CommunitySettings.name, func.count(CommunitySettings.name).label('count'))
            .filter(CommunitySettings.community_id == community_id)
            .group_by(CommunitySettings.name)
        )
        rows = await self._session.execute(query)

        return [PercentByName(name=row[0], percent=int((row[1]/total_count) * 100))
                for row in rows.all()]
