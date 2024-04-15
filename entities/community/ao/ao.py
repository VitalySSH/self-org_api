from typing import List

from sqlalchemy import select, func

from datastorage.base import DataStorage
from datastorage.database.models import UserCommunitySettings
from datastorage.interfaces import VotingParams, PercentByName


class CommunityDS(DataStorage):

    async def calculate_voting_params(self, community_id: str) -> VotingParams:
        query = select(func.avg(UserCommunitySettings.vote),
                       func.avg(UserCommunitySettings.quorum))
        query.filter(UserCommunitySettings.community_id == community_id)
        rows = await self._session.execute(query)
        vote, quorum = rows.first()

        return VotingParams(vote=int(vote), quorum=int(quorum))

    async def get_all_community_names(self, community_id: str) -> List[str]:
        query = select(UserCommunitySettings.name).distinct()
        query.filter(UserCommunitySettings.community_id == community_id)
        query.group_by(UserCommunitySettings.name)
        rows = await self._session.scalars(query)

        return list(rows.unique())

    async def get_voting_data_by_names(self, community_id: str) -> List[PercentByName]:
        query = select(func.count()).select_from(UserCommunitySettings)
        query.filter(UserCommunitySettings.community_id == community_id)
        all_rows = await self._session.scalars(query)
        data = list(all_rows)
        total_count = data[0] if data else 0
        query = (
            select(UserCommunitySettings.name,
                   func.count(UserCommunitySettings.name).label('count'))
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(UserCommunitySettings.name)
        )
        rows = await self._session.execute(query)

        return [PercentByName(name=row[0], percent=int((row[1]/total_count) * 100))
                for row in rows.all()]
