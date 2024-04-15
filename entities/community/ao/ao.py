from typing import List, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from datastorage.base import DataStorage
from datastorage.database.models import UserCommunitySettings, CommunitySettings
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
            .order_by(desc('count'))
        )
        rows = await self._session.execute(query)

        return [PercentByName(name=row[0], percent=int((row[1]/total_count) * 100))
                for row in rows.all()]

    async def change_community_settings(self, community_id: str):
        voting_params = await self.calculate_voting_params(community_id)
        vote: int = voting_params.get('vote')
        quorum: int = voting_params.get('quorum')
        name: Optional[str] = None
        names_data = await self.get_voting_data_by_names(community_id)
        name_vote: int = names_data[0].get('percent')
        if name_vote >= vote:
            name = names_data[0].get('name')
        query = (
            select(self._model).where(self._model.id == community_id)
            .options(selectinload(self._model.main_settings))
        )
        community = await self._session.scalar(query)
        community_settings: CommunitySettings = community.main_settings
        community_settings.vote = vote
        community_settings.quorum = quorum
        if name:
            community_settings.name = name
        await self._session.commit()

