import logging

from typing import List, Optional, Tuple, cast, Dict

from sqlalchemy import select, func, desc, distinct, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from core.dataclasses import PercentByName
from datastorage.ao.datastorage import AODataStorage
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.list import Filters, Operation, Filter
from datastorage.database.models import (
    Community, UserCommunitySettings, CommunitySettings,
    RelationUserCsCategories, Category, CommunityName,
    CommunityDescription, RelationUserCsUserCs
)
from datastorage.decorators import ds_async_with_new_session
from entities.community.ao.dataclasses import (
    OtherCommunitySettings, CsByPercent, UserSettingsModifiedData,
    CommunityNameData, ParentCommunity, SubCommunityData
)
from entities.status.model import Status
from entities.user_community_settings.ao.datastorage import (
    UserCommunitySettingsDS
)

logger = logging.getLogger(__name__)


class CommunityDS(AODataStorage[Community], CRUDDataStorage[Community]):
    _model = Community

    async def get_community_settings_in_percent(
            self, community_id: str
    ) -> CsByPercent:
        """Вернёт статистику в процентах по настройкам сообщества."""
        modified_data = await self._get_user_settings_modified_data(
            community_id
        )
        category_data = {
            category_id: count
            for category_id, count in modified_data.categories_data
        }
        categories_list = await self._get_categories_by_ids(
            list(category_data.keys())
        )
        categories = [
            PercentByName(
                name=category.name,
                percent=int(
                    category_data.get(category.id) /
                    modified_data.user_count * 100
                )
            )
            for category in categories_list
        ]

        child_settings_data = {
            category_id: count
            for category_id, count in modified_data.child_settings_data
        }
        child_settings = await self._get_user_settings_by_ids(
            list(child_settings_data.keys())
        )
        sub_communities = [
            PercentByName(
                name=settings.name.name,
                percent=int(child_settings_data.get(settings.id) /
                            modified_data.user_count * 100)
            ) for settings in child_settings]

        is_secret_ballot_count = await self._get_is_secret_ballot_count(
            community_id
        )
        secret_ballot_true = int(
            is_secret_ballot_count / modified_data.user_count * 100
        )
        secret_ballot = [
            PercentByName(name='Да', percent=secret_ballot_true),
            PercentByName(name='Нет', percent=100 - secret_ballot_true)
        ]

        is_minority_not_participate_count = (
            await self._get_minority_not_participate_count(community_id)
        )
        minority_not_participate_true = int(
            is_minority_not_participate_count / modified_data.user_count * 100
        )
        minority_not_participate = [
            PercentByName(name='Да', percent=minority_not_participate_true),
            PercentByName(
                name='Нет',
                percent=100 - minority_not_participate_true
            )
        ]

        is_can_offer_count = await self._get_is_can_offer_count(community_id)
        can_offer_true = int(
            is_can_offer_count / modified_data.user_count * 100
        )
        can_offer = [
            PercentByName(name='Да', percent=can_offer_true),
            PercentByName(name='Нет', percent=100 - can_offer_true)
        ]

        return CsByPercent(
            names=await self._get_voting_data_by_names(community_id),
            descriptions=await self._get_voting_data_by_desc(community_id),
            categories=categories,
            sub_communities=sub_communities,
            secret_ballot=secret_ballot,
            minority_not_participate=minority_not_participate,
            can_offer=can_offer,
        )

    async def get_community_name_data(
            self, community_id: str,
            user_id: str
    ) -> CommunityNameData:
        """Вернёт текущее наименование сообщества
        и список id родительских сообществ.
        """
        community = await self._get_community_for_name_data(community_id)
        is_blocked = not bool(list(filter(
            lambda it: it.user.id == user_id and it.is_blocked is False,
            community.user_settings or [])))
        parent_data: List[ParentCommunity] = []
        parent_community: Optional[Community] = community.parent

        while parent_community:
            parent_data.append(ParentCommunity(
                id=parent_community.id,
                name=parent_community.main_settings.name.name
            ))
            parent_community = (
                await self._get_community_with_parent(
                    parent_community.parent.id
                )
                if parent_community.parent else None
            )

        return CommunityNameData(
            name=community.main_settings.name.name,
            parent_data=parent_data,
            is_blocked=is_blocked,
        )

    async def get_sub_community_data(
            self, community_id: str, user_id: str) -> List[SubCommunityData]:
        """Вернёт данные внутренних сообществ."""
        sub_community_data: List[SubCommunityData] = []
        community: Community = await self.get(
            instance_id=community_id,
            include=[
                'main_settings.sub_communities_settings.user',
                'main_settings.sub_communities_settings.name',
                'main_settings.sub_communities_settings.description',
            ]
        )
        communities_ids = await self.get_user_community_ids_data(user_id)
        for user_settings in (community.main_settings
                                      .sub_communities_settings or []):
            sub_community = SubCommunityData(
                id=user_settings.community_id,
                title=user_settings.name.name,
                description=user_settings.description.value,
                members=await self._get_total_count_users(
                    user_settings.community_id
                ),
                isMyCommunity=bool(communities_ids.get(
                    user_settings.community_id)
                ),
                isBlocked=user_settings.is_blocked,
            )
            sub_community_data.append(sub_community)

        return sub_community_data

    @ds_async_with_new_session
    async def change_community_settings(self, community_id: str) -> None:
        voting_params = await self.calculate_voting_params(community_id)
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

        community: Community = await self._get_community(community_id)
        community_settings: CommunitySettings = community.main_settings
        system_category = await self.get_system_category()

        other_settings = await self._get_other_community_settings(
            community_id=community_id,
            vote=voting_params.vote,
            system_category_id=system_category.id if system_category else None
        )
        community_settings.vote = voting_params.vote
        community_settings.quorum = voting_params.quorum
        community_settings.significant_minority = (
            voting_params.significant_minority
        )
        community_settings.is_secret_ballot = other_settings.is_secret_ballot
        community_settings.is_can_offer = other_settings.is_can_offer
        community_settings.is_minority_not_participate = (
            other_settings.is_minority_not_participate
        )
        if name:
            community_settings.name = name
        if description:
            community_settings.description = description
        if system_category:
            other_settings.categories.insert(0, system_category)
        community_settings.categories = other_settings.categories
        community_settings.sub_communities_settings = (
            other_settings.sub_communities_settings
        )

        await self._session.commit()

    async def get_system_category(self) -> Optional[Category]:
        filters: Filters = [
            Filter(
                field='status.code',
                op=Operation.EQ,
                val=Code.SYSTEM_CATEGORY
            ),
        ]
        return await self.first(filters=filters, model=Category)


    async def _get_categories_by_ids(
            self, categories_ids: List[str]
    ) -> List[Category]:
        query = (
            select(Category).options(selectinload(Category.status))
            .filter(Category.id.in_(categories_ids))
        )
        categories_result = await self._session.scalars(query)

        return list(categories_result)

    async def _get_user_settings_by_ids(
            self, settings_ids: List[str]) -> List[UserCommunitySettings]:
        query = (
            select(UserCommunitySettings).options(
                selectinload(UserCommunitySettings.user),
                selectinload(UserCommunitySettings.name),
                selectinload(UserCommunitySettings.description),
                selectinload(UserCommunitySettings.categories),
            ).filter(UserCommunitySettings.id.in_(settings_ids))
        )
        settings_result = await self._session.scalars(query)

        return list(settings_result)

    async def _get_community(self, community_id: str) -> Optional[Community]:
        query = (
            select(self._model).where(self._model.id == community_id)
            .options(
                selectinload(self._model.main_settings)
                .selectinload(CommunitySettings.categories)
                .selectinload(Category.status),
                selectinload(self._model.main_settings)
                .selectinload(CommunitySettings.sub_communities_settings),
            )
        )

        return await self._session.scalar(query)

    async def _get_community_with_parent(
            self, community_id: Optional[str]
    ) -> Optional[Community]:
        if not community_id:
            return None

        query = (
            select(self._model)
            .where(self._model.id == community_id)
            .options(
                selectinload(self._model.parent)
                .selectinload(self._model.main_settings)
                .selectinload(CommunitySettings.name)
            )
        )

        return await self._session.scalar(query)

    async def _get_community_for_name_data(
            self, community_id: str
    ) -> Optional[Community]:
        query = (
            select(self._model).where(self._model.id == community_id)
            .options(
                selectinload(self._model.parent)
                .selectinload(self._model.main_settings)
                .selectinload(CommunitySettings.name),
                selectinload(self._model.user_settings)
                .selectinload(UserCommunitySettings.user),
                selectinload(self._model.main_settings)
                .selectinload(CommunitySettings.name)
            )
        )

        return await self._session.scalar(query)

    async def get_current_user_community_ids(self, user_id: str) -> List[str]:
        query = (
            select(distinct(UserCommunitySettings.community_id))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.user_id == user_id)
        )
        community_ids = await self._session.execute(query)

        return [row[0] for row in community_ids.all()]

    async def get_user_community_ids_data(
            self, user_id: str
    ) -> Dict[str, str]:
        query = (
            select(distinct(UserCommunitySettings.community_id))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.user_id == user_id)
        )
        community_ids = await self._session.execute(query)

        return {row[0]: row[0] for row in community_ids.all()}

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
            self, community_id: str
    ) -> Optional[Tuple[CommunityDescription, int]]:
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

    async def _get_voting_data_by_names(
            self, community_id: str
    ) -> List[PercentByName]:
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

        return [
            PercentByName(name=name, percent=int((count / total_count) * 100))
            for name, count in name_data.all()]

    async def _get_voting_data_by_desc(
            self, community_id: str
    ) -> List[PercentByName]:
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

        return [
            PercentByName(name=desc_, percent=int((count / total_count) * 100))
            for desc_, count in desc_data.all()]

    async def _get_user_settings_modified_data(
            self, community_id: str) -> UserSettingsModifiedData:
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
            .join(Category,
                  RelationUserCsCategories.to_id == Category.id)
            .join(Status,
                  Category.status_id == Status.id)
            .where(
                RelationUserCsCategories.from_id.in_(user_cs_ids),
                Status.code != Code.SYSTEM_CATEGORY
            )
            .group_by(RelationUserCsCategories.to_id)
            .order_by(desc('count'))
        )
        categories = await self._session.execute(categories_query)

        child_settings_query = (
            select(RelationUserCsUserCs.to_id,
                   func.count(RelationUserCsUserCs.to_id).label('count'))
            .where(RelationUserCsUserCs.from_id.in_(user_cs_ids))
            .group_by(RelationUserCsUserCs.to_id)
            .order_by(desc('count'))
        )
        child_settings = await self._session.execute(child_settings_query)

        return UserSettingsModifiedData(
            user_count=user_count,
            categories_data=cast(List[Tuple[str, int]], categories.all()),
            child_settings_data=cast(List[Tuple[str, int]],
                                     child_settings.all()),
        )

    async def _get_other_community_settings(
            self, community_id: str,
            vote: int,
            system_category_id: Optional[str],
    ) -> OtherCommunitySettings:
        all_category_ids = []
        selected_category_ids: Dict[str, str] = {}
        all_user_settings_ids = []
        selected_user_settings_ids: Dict[str, str] = {}
        modified_data = await self._get_user_settings_modified_data(
            community_id
        )
        for category_id, count in modified_data.categories_data:
            all_category_ids.append(category_id)
            if int(count / modified_data.user_count * 100) >= vote:
                selected_category_ids[category_id] = category_id

        for settings_id, count in modified_data.child_settings_data:
            all_user_settings_ids.append(settings_id)
            if int(count / modified_data.user_count * 100) >= vote:
                selected_user_settings_ids[settings_id] = settings_id

        categories = await self._get_selected_categories(
            all_ids=all_category_ids,
            selected_ids=selected_category_ids,
            community_id=community_id,
            system_category_id=system_category_id,
        )
        sub_communities_settings = await self._get_selected_sub_user_settings(
            ids=all_user_settings_ids, selected_ids=selected_user_settings_ids
        )

        is_secret_ballot_count = await self._get_is_secret_ballot_count(
            community_id
        )
        is_secret_ballot = int(
            is_secret_ballot_count / modified_data.user_count * 100
        ) >= vote

        is_can_offer_count = await self._get_is_can_offer_count(community_id)
        is_can_offer = int(
            is_can_offer_count / modified_data.user_count * 100
        ) >= vote

        is_minority_not_participate_count = (
            await self._get_minority_not_participate_count(community_id)
        )
        is_minority_not_participate = int(
            is_minority_not_participate_count / modified_data.user_count * 100
        ) >= vote

        return OtherCommunitySettings(
            categories=categories,
            sub_communities_settings=sub_communities_settings,
            is_secret_ballot=is_secret_ballot,
            is_minority_not_participate=is_minority_not_participate,
            is_can_offer=is_can_offer,
        )

    async def _get_selected_categories(
            self, all_ids: List[str],
            selected_ids: Dict[str, str],
            community_id: str,
            system_category_id: Optional[str],
    ) -> List[Category]:
        categories: List[Category] = []
        if all_ids:
            query = (
                select(Category)
                .options(selectinload(Category.status))
                .filter(Category.id.in_(all_ids)))
            categories_data = await self._session.scalars(query)
            selected_status = await self.get_status_by_code(
                Code.CATEGORY_SELECTED
            )
            on_cons_status = await self.get_status_by_code(
                Code.ON_CONSIDERATION
            )
            for category in list(categories_data):
                if selected_ids.get(category.id):
                    if category.status.code != Code.CATEGORY_SELECTED:
                        category.status = selected_status
                        await self._update_category_from_old_category(
                            community_id
                        )
                    categories.append(category)
                else:
                    if category.status.code != Code.ON_CONSIDERATION:
                        if system_category_id:
                            await self._add_old_category(
                                new_category_id=system_category_id,
                                old_category_id=category.id,
                                community_id=community_id,
                            )
                        category.status = on_cons_status

        return categories

    async def _get_selected_sub_user_settings(
            self, ids: List[str],
            selected_ids: Dict[str, str],
    ) -> List[UserCommunitySettings]:
        sub_user_settings: List[UserCommunitySettings] = []
        if ids:
            query = (
                select(UserCommunitySettings)
                .options(
                    selectinload(UserCommunitySettings.user),
                    selectinload(UserCommunitySettings.name),
                    selectinload(UserCommunitySettings.description),
                    selectinload(UserCommunitySettings.categories),
                    selectinload(UserCommunitySettings.adding_members),
                ).filter(UserCommunitySettings.id.in_(ids)))
            sub_user_settings_data = await self._session.scalars(query)
            all_sub_user_settings = list(sub_user_settings_data)
            ucs_ds = UserCommunitySettingsDS(self._session)
            for user_settings in all_sub_user_settings:
                if selected_ids.get(user_settings.id):
                    community = await ucs_ds.get_or_create_child_community(
                        user_settings
                    )
                    community.is_blocked = False
                    sub_user_settings.append(user_settings)
                else:
                    community = await ucs_ds.get_community(
                        user_settings.community_id
                    )
                    if community:
                        community.is_blocked = True

        return sub_user_settings

    async def get_status_by_code(self, code: str) -> Optional[Status]:
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

    async def _get_minority_not_participate_count(
            self, community_id: str
    ) -> int:
        count_query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.is_minority_not_participate.is_(True),
                UserCommunitySettings.is_blocked.is_not(True),
                UserCommunitySettings.community_id == community_id,
            )
        )
        return await self._session.scalar(count_query)

    async def _add_old_category(
            self, new_category_id: str,
            old_category_id: str,
            community_id: str,
    ) -> None:
        query_rule = text("""
            UPDATE public.rule
            SET category_id = :new_category_id, old_category_id = :old_category_id
            WHERE community_id = :community_id
        """)

        query_initiative = text("""
            UPDATE public.initiative
            SET category_id = :new_category_id, old_category_id = :old_category_id
            WHERE community_id = :community_id
        """)

        query_challenge = text("""
            UPDATE public.challenge
            SET category_id = :new_category_id, old_category_id = :old_category_id
            WHERE community_id = :community_id
        """)

        try:
            async with self._session.begin_nested():

                await self._session.execute(
                    query_rule,
                    {
                        'new_category_id': new_category_id,
                        'old_category_id': old_category_id,
                        'community_id': community_id,
                    }
                )
                await self._session.execute(
                    query_initiative,
                    {
                        'new_category_id': new_category_id,
                        'old_category_id': old_category_id,
                        'community_id': community_id,
                    }
                )
                await self._session.execute(
                    query_challenge,
                    {
                        'new_category_id': new_category_id,
                        'old_category_id': old_category_id,
                        'community_id': community_id,
                    }
                )

        except SQLAlchemyError as e:
            logger.error(
                f'Ошибка при обновлении пользовательских'
                f' результатов голосований: {e}.\n'
                f'Параметры: new_category_id={new_category_id}, '
                f'old_category_id={old_category_id}, '
                f'community_id={community_id}'
            )
            await self._session.rollback()

    async def _update_category_from_old_category(self, community_id: str):
        query_rule = text("""
            UPDATE public.rule
            SET 
                category_id = old_category_id,
                old_category_id = NULL
            WHERE community_id = :community_id
              AND old_category_id IS NOT NULL
        """)

        query_initiative = text("""
            UPDATE public.initiative
            SET 
                category_id = old_category_id,
                old_category_id = NULL
            WHERE community_id = :community_id
              AND old_category_id IS NOT NULL
        """)

        query_challenge = text("""
            UPDATE public.challenge
            SET 
                category_id = old_category_id,
                old_category_id = NULL
            WHERE community_id = :community_id
              AND old_category_id IS NOT NULL
        """)

        try:
            async with self._session.begin_nested():

                await self._session.execute(
                    query_rule,
                    {'community_id': community_id}
                )
                await self._session.execute(
                    query_initiative,
                    {'community_id': community_id}
                )
                await self._session.execute(
                    query_challenge,
                    {'community_id': community_id}
                )

            await self._session.commit()

        except SQLAlchemyError as e:
            logger.error(
                f'Ошибка при обновлении категорий для записей с '
                f'community_id={community_id}: {e}'
            )
            await self._session.rollback()
