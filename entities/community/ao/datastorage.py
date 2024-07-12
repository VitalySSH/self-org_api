from typing import List, Optional, Tuple, cast

from sqlalchemy import select, func, desc, asc, distinct
from sqlalchemy.orm import selectinload

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import (
    Community, UserCommunitySettings, CommunitySettings,
    RelationUserCsCategories, InitiativeCategory, CommunityName, CommunityDescription
)
from datastorage.decorators import ds_async_with_new_session
from datastorage.interfaces import VotingParams, PercentByName, CsByPercent
from entities.community.ao.dataclasses import OtherCommunitySettings
from entities.community_description.crud.schemas import CommunityDescRead
from entities.community_name.crud.schemas import CommunityNameRead
from entities.user.model import User


class CommunityDS(CRUDDataStorage[Community]):

    async def calculate_voting_params(self, community_id: str) -> VotingParams:
        query = (
            select(func.avg(UserCommunitySettings.vote),
                   func.avg(UserCommunitySettings.quorum))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.community_id == community_id)
        )
        rows = await self._session.execute(query)
        vote, quorum = rows.first()

        return VotingParams(vote=int(vote), quorum=int(quorum))

    async def get_community_names(self, community_id: str) -> List[CommunityNameRead]:
        query = select(CommunityName)
        query.filter(CommunityName.community_id == community_id)
        query.order_by(asc(CommunityName.name))
        names = await self._session.scalars(query)

        return [name.to_read_schema() for name in names]

    async def get_community_descriptions(self, community_id: str) -> List[CommunityDescRead]:
        query = select(CommunityDescription)
        query.filter(CommunityDescription.community_id == community_id)
        descriptions = await self._session.scalars(query)

        return [description.to_read_schema() for description in descriptions]

    async def _get_first_community_name(
            self, community_id: str) -> Optional[Tuple[CommunityName, int]]:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        total_count = await self._session.scalar(query)
        query = (
            select(CommunityName,
                   func.count(CommunityName.name).label('count'))
            .select_from(UserCommunitySettings, CommunityName)
            .join(CommunityName)
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(CommunityName.name, CommunityName)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(query)
        names = name_data.all()
        if names:
            return names[0][0], int((names[0][1] / total_count) * 100)
        return None

    async def _get_first_community_desc(
            self, community_id: str) -> Optional[Tuple[CommunityDescription, int]]:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        total_count = await self._session.scalar(query)
        query = (
            select(CommunityDescription,
                   func.count(CommunityDescription.value).label('count'))
            .select_from(UserCommunitySettings, CommunityDescription)
            .join(CommunityDescription)
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(CommunityDescription.value, CommunityDescription)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(query)
        names = name_data.all()
        if names:
            return names[0][0], int((names[0][1] / total_count) * 100)
        return None

    async def _get_voting_data_by_names(self, community_id: str) -> List[PercentByName]:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        total_count = await self._session.scalar(query)
        query = (
            select(CommunityName.name,
                   func.count(CommunityName.name).label('count'))
            .select_from(UserCommunitySettings, CommunityName)
            .join(CommunityName)
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(CommunityName.name)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(query)

        return [PercentByName(name=name, percent=int((count / total_count) * 100))
                for name, count in name_data.all()]

    async def _get_voting_data_by_desc(self, community_id: str) -> List[PercentByName]:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .filter(UserCommunitySettings.community_id == community_id)
        )
        total_count = await self._session.scalar(query)
        query = (
            select(CommunityDescription.value,
                   func.count(CommunityDescription.value).label('count'))
            .select_from(UserCommunitySettings, CommunityDescription)
            .join(CommunityDescription)
            .filter(UserCommunitySettings.community_id == community_id)
            .group_by(CommunityDescription.value)
            .order_by(desc('count'))
        )
        desc_data = await self._session.execute(query)

        return [PercentByName(name=desc_, percent=int((count / total_count) * 100))
                for desc_, count in desc_data.all()]

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
            .filter(UserCommunitySettings.is_minority_not_participate.is_(True))
        )
        is_minority_not_participate_count = await self._session.scalar(query)
        minority_not_participate_true = int(is_minority_not_participate_count / user_count * 100)
        minority_not_participate = [
            PercentByName(name='Да', percent=minority_not_participate_true),
            PercentByName(name='Нет', percent=100 - minority_not_participate_true)
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
            descriptions=await self._get_voting_data_by_desc(community_id),
            categories=categories,
            secret_ballot=secret_ballot,
            minority_not_participate=minority_not_participate,
            can_offer=can_offer,
        )

    @ds_async_with_new_session
    async def change_community_settings(self, community_id: str) -> None:
        voting_params = await self.calculate_voting_params(community_id)
        vote: int = voting_params.get('vote')
        quorum: int = voting_params.get('quorum')
        name: Optional[CommunityName] = None
        description: Optional[CommunityDescription] = None
        names_data = await self._get_first_community_name(community_id)
        if names_data:
            name_vote = names_data[1]
            if name_vote >= vote:
                name = names_data[0]
        desc_data = await self._get_first_community_desc(community_id)
        if desc_data:
            desc_vote = desc_data[1]
            if desc_vote >= vote:
                description = desc_data[0]

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
        community_settings.is_minority_not_participate = other_settings.is_minority_not_participate
        if name:
            community_settings.name = name
        if description:
            community_settings.description = description
        if other_settings.categories:
            community_settings.init_categories = other_settings.categories
        await self._session.commit()

    async def _get_user_init_categories(
            self, community_id: str) -> Tuple[List[Tuple[str, int]], int]:
        query = (
            select(UserCommunitySettings.id)
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.community_id == community_id)
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
            .where(
                UserCommunitySettings.is_secret_ballot.is_(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        is_secret_ballot_count = await self._session.scalar(query)
        is_secret_ballot = int(is_secret_ballot_count / user_count * 100) >= vote

        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_can_offer.is_(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        is_can_offer_count = await self._session.scalar(query)
        is_can_offer = int(is_can_offer_count / user_count * 100) >= vote

        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_minority_not_participate.is_(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        is_minority_not_participate_count = await self._session.scalar(query)
        is_minority_not_participate = int(
            is_minority_not_participate_count / user_count * 100) >= vote

        return OtherCommunitySettings(
            categories=categories,
            is_secret_ballot=is_secret_ballot,
            is_minority_not_participate=is_minority_not_participate,
            is_can_offer=is_can_offer,
        )

    async def get_current_user_community_ids(self, user: User) -> List[str]:
        query = (
            select(distinct(UserCommunitySettings.community_id))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.user_id == user.id)
        )
        community_ids = await self._session.execute(query)

        return [row[0] for row in community_ids.all()]
