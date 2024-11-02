from typing import List, Optional, Tuple, cast, Dict

from sqlalchemy import select, func, desc, distinct
from sqlalchemy.orm import selectinload

from core.dataclasses import BaseVotingParams, PercentByName
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import (
    Community, UserCommunitySettings, CommunitySettings, RelationUserCsCategories, Category,
    CommunityName, CommunityDescription
)
from datastorage.decorators import ds_async_with_new_session
from entities.community.ao.dataclasses import OtherCommunitySettings, CsByPercent
from entities.status.model import Status
from auth.models.user import User


class CommunityDS(CRUDDataStorage[Community]):

    async def get_community_settings_in_percent(self, community_id: str) -> CsByPercent:
        categories_data, user_count = await self._get_user_categories(community_id)
        category_data = {category_id: count for category_id, count in categories_data}
        query = (
            select(Category).options(selectinload(Category.status))
            .filter(Category.id.in_(list(category_data.keys())))
        )
        categories_result = await self._session.scalars(query)
        categories_list = list(categories_result)
        categories = [PercentByName(name=category.name,
                                    percent=int(category_data.get(category.id) / user_count * 100))
                      for category in categories_list
                      if category.status.code != Code.SYSTEM_CATEGORY]

        is_secret_ballot_count = await self._get_is_secret_ballot_count(community_id)
        secret_ballot_true = int(is_secret_ballot_count / user_count * 100)
        secret_ballot = [
            PercentByName(name='Да', percent=secret_ballot_true),
            PercentByName(name='Нет', percent=100 - secret_ballot_true)
        ]

        is_minority_not_participate_count = await self._get_minority_not_participate_count(
            community_id)
        minority_not_participate_true = int(is_minority_not_participate_count / user_count * 100)
        minority_not_participate = [
            PercentByName(name='Да', percent=minority_not_participate_true),
            PercentByName(name='Нет', percent=100 - minority_not_participate_true)
        ]

        is_can_offer_count = await self._get_is_can_offer_count(community_id)
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
        voting_params: BaseVotingParams = await self._calculate_voting_params(community_id)
        name: Optional[CommunityName] = None
        description: Optional[CommunityDescription] = None
        names_data = await self._get_first_community_name(community_id)
        if names_data:
            name_vote = names_data[1]
            if name_vote >= voting_params.vote:
                name = names_data[0]
        desc_data = await self._get_first_community_desc(community_id)
        if desc_data:
            desc_vote = desc_data[1]
            if desc_vote >= voting_params.vote:
                description = desc_data[0]

        query = (
            select(self._model).where(self._model.id == community_id)
            .options(selectinload(self._model.main_settings)
                     .selectinload(CommunitySettings.categories)
                     .selectinload(Category.status))
        )
        community = await self._session.scalar(query)
        other_settings: OtherCommunitySettings = await self._get_other_community_settings(
            community_id=community_id, vote=voting_params.vote)
        community_settings: CommunitySettings = community.main_settings
        community_settings.vote = voting_params.vote
        community_settings.quorum = voting_params.quorum
        community_settings.significant_minority = voting_params.significant_minority
        community_settings.is_secret_ballot = other_settings.is_secret_ballot
        community_settings.is_can_offer = other_settings.is_can_offer
        community_settings.is_minority_not_participate = other_settings.is_minority_not_participate
        if name:
            community_settings.name = name
        if description:
            community_settings.description = description
        if other_settings.categories:
            community_settings.categories = other_settings.categories
        await self._session.commit()

    async def get_current_user_community_ids(self, user: User) -> List[str]:
        query = (
            select(distinct(UserCommunitySettings.community_id))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.user_id == user.id)
        )
        community_ids = await self._session.execute(query)

        return [row[0] for row in community_ids.all()]

    async def _calculate_voting_params(self, community_id: str) -> BaseVotingParams:
        query = (
            select(func.avg(UserCommunitySettings.vote),
                   func.avg(UserCommunitySettings.quorum),
                   func.avg(UserCommunitySettings.significant_minority))
            .select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        rows = await self._session.execute(query)
        vote, quorum, significant_minority = rows.first()

        return BaseVotingParams(
            vote=int(vote), quorum=int(quorum),
            significant_minority=int(significant_minority))

    async def _get_first_community_name(
            self, community_id: str) -> Optional[Tuple[CommunityName, int]]:
        total_count = await self._get_total_count_users(community_id)
        name_data_query = (
            select(CommunityName,
                   func.count(CommunityName.name).label('count'))
            .select_from(UserCommunitySettings, CommunityName)
            .join(CommunityName)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
            .group_by(CommunityName.name, CommunityName)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(name_data_query)
        names = name_data.all()
        if names:
            return names[0][0], int((names[0][1] / total_count) * 100)

        return None

    async def _get_first_community_desc(
            self, community_id: str) -> Optional[Tuple[CommunityDescription, int]]:
        total_count = await self._get_total_count_users(community_id)
        name_data_query = (
            select(CommunityDescription,
                   func.count(CommunityDescription.value).label('count'))
            .select_from(UserCommunitySettings, CommunityDescription)
            .join(CommunityDescription)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
            .group_by(CommunityDescription.value, CommunityDescription)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(name_data_query)
        names = name_data.all()
        if names:
            return names[0][0], int((names[0][1] / total_count) * 100)

        return None

    async def _get_voting_data_by_names(self, community_id: str) -> List[PercentByName]:
        total_count = await self._get_total_count_users(community_id)
        name_data_query = (
            select(CommunityName.name,
                   func.count(CommunityName.name).label('count'))
            .select_from(UserCommunitySettings, CommunityName)
            .join(CommunityName)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
            .group_by(CommunityName.name)
            .order_by(desc('count'))
        )
        name_data = await self._session.execute(name_data_query)

        return [PercentByName(name=name, percent=int((count / total_count) * 100))
                for name, count in name_data.all()]

    async def _get_voting_data_by_desc(self, community_id: str) -> List[PercentByName]:
        total_count = await self._get_total_count_users(community_id)
        desc_data_query = (
            select(CommunityDescription.value,
                   func.count(CommunityDescription.value).label('count'))
            .select_from(UserCommunitySettings, CommunityDescription)
            .join(CommunityDescription)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
            .group_by(CommunityDescription.value)
            .order_by(desc('count'))
        )
        desc_data = await self._session.execute(desc_data_query)

        return [PercentByName(name=desc_, percent=int((count / total_count) * 100))
                for desc_, count in desc_data.all()]

    async def _get_user_categories(self, community_id: str) -> Tuple[List[Tuple[str, int]], int]:
        user_cs_query = (
            select(UserCommunitySettings.id)
            .select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        user_cs = await self._session.scalars(user_cs_query)
        user_cs_ids = list(user_cs)
        user_count = len(user_cs_ids)
        categories_query = (
            select(RelationUserCsCategories.to_id,
                   func.count(RelationUserCsCategories.to_id).label('count'))
            .where(RelationUserCsCategories.from_id.in_(user_cs_ids))
            .group_by(RelationUserCsCategories.to_id)
            .order_by(desc('count'))
        )
        categories = await self._session.execute(categories_query)

        return cast(List[Tuple[str, int]], categories.all()), user_count

    async def _get_other_community_settings(
            self, community_id: str, vote: int) -> OtherCommunitySettings:
        all_category_ids = []
        category_ids: Dict[str, str] = {}
        category_data, user_count = await self._get_user_categories(community_id)
        for category_id, count in category_data:
            all_category_ids.append(category_id)
            if int(count / user_count * 100) >= vote:
                category_ids[category_id] = category_id

        categories: List[Category] = []
        if all_category_ids:
            query = (
                select(Category)
                .options(selectinload(Category.status))
                .filter(Category.id.in_(all_category_ids)))
            categories_data = await self._session.scalars(query)
            all_categories = list(categories_data)
            selected_status = await self._get_status_by_code(Code.CATEGORY_SELECTED)
            on_cons_status = await self._get_status_by_code(Code.ON_CONSIDERATION)
            for category in all_categories:
                if category_ids.get(category.id):
                    if category.status.code == Code.SYSTEM_CATEGORY:
                        continue
                    elif category.status.code != Code.CATEGORY_SELECTED:
                        category.status = selected_status
                    categories.append(category)
                else:
                    category.status = on_cons_status

        is_secret_ballot_count = await self._get_is_secret_ballot_count(community_id)
        is_secret_ballot = int(is_secret_ballot_count / user_count * 100) >= vote

        is_can_offer_count = await self._get_is_can_offer_count(community_id)
        is_can_offer = int(is_can_offer_count / user_count * 100) >= vote

        is_minority_not_participate_count = await self._get_minority_not_participate_count(
            community_id)
        is_minority_not_participate = int(
            is_minority_not_participate_count / user_count * 100) >= vote

        return OtherCommunitySettings(
            categories=categories,
            is_secret_ballot=is_secret_ballot,
            is_minority_not_participate=is_minority_not_participate,
            is_can_offer=is_can_offer,
        )

    async def _get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def _get_total_count_users(self, community_id: str) -> int:
        count_query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        return await self._session.scalar(count_query)

    async def _get_is_secret_ballot_count(self, community_id: str) -> int:
        count_query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_secret_ballot.is_(True),
                UserCommunitySettings.is_blocked.is_not(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        return await self._session.scalar(count_query)

    async def _get_is_can_offer_count(self, community_id: str) -> int:
        count_query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_can_offer.is_(True),
                UserCommunitySettings.is_blocked.is_not(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        return await self._session.scalar(count_query)

    async def _get_minority_not_participate_count(self, community_id: str) -> int:
        count_query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_minority_not_participate.is_(True),
                UserCommunitySettings.is_blocked.is_not(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        return await self._session.scalar(count_query)
