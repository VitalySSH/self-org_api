from typing import List, Optional, Tuple, cast

from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from datastorage.base import DataStorage
from datastorage.database.models import (
    Community, UserCommunitySettings, CommunitySettings,
    RelationUserCsCategories, InitiativeCategory
)
from datastorage.decorators import ds_async_with_session
from datastorage.interfaces import VotingParams, PercentByName, CsByPercent
from entities.community.ao.dataclasses import OtherCommunitySettings


class CommunityDS(DataStorage[Community]):

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

    async def _get_voting_data_by_names(self, community_id: str) -> List[PercentByName]:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        total_count = await self._session.scalar(query)
        query = (
            select(UserCommunitySettings.name,
                   func.count(UserCommunitySettings.name).label('count'))
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(UserCommunitySettings.name)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(query)

        return [PercentByName(name=name, percent=int((count / total_count) * 100))
                for name, count in name_data.all()]

    async def get_community_settings_in_percent(self, community_id: str) -> CsByPercent:
        categories_data, user_count = await self._get_user_init_categories(community_id)
        category_data = {category_id: count for category_id, count in categories_data}
        query = (select(InitiativeCategory)
                 .filter(InitiativeCategory.id.in_(list(category_data.keys()))))
        categories_result = await self._session.scalars(query)
        categories_list = list(categories_result)
        categories = [PercentByName(name=category.name, 
                                    percent=int(category_data.get(category.id) / user_count * 100)) 
                      for category in categories_list]
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.is_secret_ballot.is_(True))
        )
        is_secret_ballot_count = await self._session.scalar(query)
        secret_ballot_true = int(is_secret_ballot_count / user_count * 100)
        secret_ballot = [
            PercentByName(name='Да', percent=secret_ballot_true),
            PercentByName(name='Нет', percent=100 - secret_ballot_true)
        ]
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.is_can_offer.is_(True))
        )
        is_can_offer_count = await self._session.scalar(query)
        can_offer_true = int(is_can_offer_count / user_count * 100)
        can_offer = [
            PercentByName(name='Да', percent=can_offer_true),
            PercentByName(name='Нет', percent=100 - can_offer_true)
        ]

        return CsByPercent(
            names=await self._get_voting_data_by_names(community_id),
            categories=categories,
            secret_ballot=secret_ballot,
            can_offer=can_offer,
        )

    @ds_async_with_session()
    async def change_community_settings(self, community_id: str) -> None:
        voting_params = await self.calculate_voting_params(community_id)
        vote: int = voting_params.get('vote')
        quorum: int = voting_params.get('quorum')
        name: Optional[str] = None
        names_data = await self._get_voting_data_by_names(community_id)
        name_vote: int = names_data[0].get('percent')
        if name_vote >= vote:
            name = names_data[0].get('name')
        query = (
            select(self._model).where(self._model.id == community_id)
            .options(selectinload(self._model.main_settings)
                     .selectinload(CommunitySettings.init_categories))
        )
        community = await self._session.scalar(query)
        other_settings = await self._get_other_community_settings(
            community_id=community_id, vote=vote)
        community_settings: CommunitySettings = community.main_settings
        community_settings.vote = vote
        community_settings.quorum = quorum
        community_settings.is_secret_ballot = other_settings.is_secret_ballot
        community_settings.is_can_offer = other_settings.is_can_offer
        if name:
            community_settings.name = name
        if other_settings.categories:
            community_settings.init_categories = other_settings.categories
        await self._session.commit()

    async def _get_user_init_categories(
            self, community_id: str) -> Tuple[List[Tuple[str, int]], int]:
        query = (
            select(UserCommunitySettings.id)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        user_cs = await self._session.scalars(query)
        user_cs_ids = list(user_cs)
        user_count = len(user_cs_ids)
        query = (
            select(RelationUserCsCategories.to_id,
                   func.count(RelationUserCsCategories.to_id).label('count'))
            .filter(RelationUserCsCategories.from_id.in_(user_cs_ids))
            .group_by(RelationUserCsCategories.to_id)
            .order_by(desc('count'))
        )
        init_categories = await self._session.execute(query)

        return cast(List[Tuple[str, int]], init_categories.all()), user_count

    async def _get_other_community_settings(
            self, community_id: str, vote: int) -> OtherCommunitySettings:
        category_ids = []
        init_categories, user_count = await self._get_user_init_categories(community_id)
        for category_id, count in init_categories:
            if int(count / user_count * 100) >= vote:
                category_ids.append(category_id)

        categories: List[InitiativeCategory] = []
        if category_ids:
            query = select(InitiativeCategory).filter(InitiativeCategory.id.in_(category_ids))
            categories_data = await self._session.scalars(query)
            categories = list(categories_data)

        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.is_secret_ballot.is_(True))
        )
        is_secret_ballot_count = await self._session.scalar(query)
        is_secret_ballot = int(is_secret_ballot_count / user_count * 100) >= vote

        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.is_can_offer.is_(True))
        )
        is_can_offer_count = await self._session.scalar(query)
        is_can_offer = int(is_can_offer_count / user_count * 100) >= vote

        return OtherCommunitySettings(
            categories=categories,
            is_secret_ballot=is_secret_ballot,
            is_can_offer=is_can_offer,
        )
