import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, insert, Insert
from sqlalchemy.orm import selectinload

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import (
    RequestMember, RelationUserCsRequestMember, RelationCommunityUCs
)
from datastorage.decorators import ds_async_with_new_session
from datastorage.interfaces import RelationRow
from datastorage.utils import build_uuid
from entities.community.model import Community
from entities.community_description.model import CommunityDescription
from entities.community_name.model import CommunityName
from entities.community_settings.model import CommunitySettings
from entities.initiative_category.model import InitiativeCategory
from entities.status.model import Status
from entities.user_community_settings.ao.dataclasses import CreatingCommunity
from entities.user_community_settings.model import UserCommunitySettings

logger = logging.getLogger(__name__)


class UserCommunitySettingsDS(CRUDDataStorage[RequestMember]):

    async def create_community(self, data_to_create: CreatingCommunity) -> None:
        data_to_create.community_id = build_uuid()
        await self._create_community_name(data_to_create)
        await self._create_community_description(data_to_create)
        await self._create_init_categories(data_to_create)
        user_settings = await self._create_user_settings(data_to_create)
        main_settings = await self._create_main_settings(data_to_create)
        community = Community()
        community.id = data_to_create.community_id
        community.main_settings = main_settings
        community.user_settings = [user_settings]
        community.creator = data_to_create.user
        self._session.add(community)
        await self._session.flush([community])
        await self._session.refresh(community)
        data_to_create.community_obj = community
        request_member = await self._create_request_member(data_to_create)
        main_settings.adding_members = [request_member]
        child_request_member = await self._create_child_request_member(
            data_to_create=data_to_create, request_member=request_member)
        user_settings.adding_members = [child_request_member]
        await self._session.commit()

    @ds_async_with_new_session
    async def update_data_after_join(
            self, user_settings_id: str,
            community_id: str, request_member_id: str) -> None:
        await self._add_to_main_settings(
            user_settings_id=user_settings_id, community_id=community_id)
        await self._update_parent_request_member(request_member_id)
        await self._create_child_request_members(
            community_id=community_id, user_settings_id=user_settings_id)
        await self._session.commit()

    async def _create_community_name(self, data_to_create: CreatingCommunity) -> None:
        community_name = CommunityName()
        community_name.name = data_to_create.name
        community_name.community_id = data_to_create.community_id
        community_name.creator_id = data_to_create.user.id
        community_name.is_readonly = True
        self._session.add(community_name)
        await self._session.flush([community_name])
        await self._session.refresh(community_name)
        data_to_create.name_obj = community_name

    async def _create_community_description(self, data_to_create: CreatingCommunity) -> None:
        description = CommunityDescription()
        description.value = data_to_create.description
        description.community_id = data_to_create.community_id
        description.creator_id = data_to_create.user.id
        description.is_readonly = True
        self._session.add(description)
        await self._session.flush([description])
        await self._session.refresh(description)
        data_to_create.description_obj = description

    async def _create_init_categories(self, data_to_create: CreatingCommunity) -> None:
        init_categories: List[InitiativeCategory] = []
        init_category_names = data_to_create.init_categories
        init_category_names.insert(0, 'Общие вопросы')
        category_status: Optional[Status] = None
        for idx, category_name in enumerate(init_category_names):
            if idx == 0:
                status = await self._get_status_by_code('system_category')
            else:
                status = category_status
            if not status:
                status = await self._get_status_by_code('category_selected')
                category_status = status
            init_category = InitiativeCategory()
            init_category.name = category_name
            init_category.community_id = data_to_create.community_id
            init_category.creator = data_to_create.user
            init_category.status = status
            self._session.add(init_category)
            await self._session.flush([init_category])
            await self._session.refresh(init_category)
            init_categories.append(init_category)

        data_to_create.init_categories_objs = init_categories

    async def _create_main_settings(self, data_to_create: CreatingCommunity) -> CommunitySettings:
        settings = CommunitySettings()
        settings.name = data_to_create.name_obj
        settings.description = data_to_create.description_obj
        settings.quorum = data_to_create.settings.get('quorum')
        settings.vote = data_to_create.settings.get('vote')
        settings.is_secret_ballot = data_to_create.settings.get('is_secret_ballot')
        settings.is_can_offer = data_to_create.settings.get('is_can_offer')
        settings.is_minority_not_participate = data_to_create.settings.get(
            'is_minority_not_participate')
        settings.init_categories = data_to_create.init_categories_objs
        self._session.add(settings)
        await self._session.flush([settings])
        await self._session.refresh(settings)

        return settings

    async def _create_user_settings(
            self, data_to_create: CreatingCommunity) -> UserCommunitySettings:
        settings = UserCommunitySettings()
        settings.user = data_to_create.user
        settings.community_id = data_to_create.community_id
        settings.name = data_to_create.name_obj
        settings.description = data_to_create.description_obj
        settings.quorum = data_to_create.settings.get('quorum')
        settings.vote = data_to_create.settings.get('vote')
        settings.is_secret_ballot = data_to_create.settings.get('is_secret_ballot')
        settings.is_can_offer = data_to_create.settings.get('is_can_offer')
        settings.is_minority_not_participate = data_to_create.settings.get(
            'is_minority_not_participate')
        settings.is_not_delegate = data_to_create.settings.get('is_not_delegate')
        settings.is_default_add_member = data_to_create.settings.get('is_default_add_member')
        settings.init_categories = data_to_create.init_categories_objs
        self._session.add(settings)
        await self._session.flush([settings])
        await self._session.refresh(settings)

        return settings

    async def _create_request_member(self, data_to_create: CreatingCommunity) -> RequestMember:
        request_member = RequestMember()
        request_member.member = data_to_create.user
        request_member.community = data_to_create.community_obj
        request_member.status = await self._get_status_by_code('community_member')
        request_member.vote = True
        request_member.reason = 'Создатель сообщества'
        self._session.add(request_member)
        await self._session.flush([request_member])
        await self._session.refresh(request_member)

        return request_member

    async def _create_child_request_member(
            self, data_to_create: CreatingCommunity,
            request_member: RequestMember) -> RequestMember:
        child_request_member = self._create_copy_request_member(request_member)
        child_request_member.parent_id = request_member.id
        status = await self._get_status_by_code('voted')
        child_request_member.community = data_to_create.community_obj
        child_request_member.member = data_to_create.user
        child_request_member.status = status
        self._session.add(child_request_member)
        await self._session.flush([child_request_member])
        await self._session.refresh(child_request_member)

        return child_request_member

    async def _add_to_main_settings(self, user_settings_id: str, community_id: str, ) -> None:
        value = RelationRow(
            id=build_uuid(),
            from_id=community_id,
            to_id=user_settings_id,
        )
        stmt: Insert = insert(RelationCommunityUCs).values(**value)
        stmt.compile()
        await self._session.execute(stmt)

    async def _update_parent_request_member(self, request_member_id: str) -> None:
        parent_request_member = await self._get_request_member(request_member_id)
        parent_status = await self._get_status_by_code('community_member')
        parent_request_member.status = parent_status
        parent_request_member.updated = datetime.now()
        await self._session.flush([parent_request_member])

    async def _get_request_member(self, request_member_id: str) -> Optional[RequestMember]:
        query = (
            select(RequestMember)
            .options(
                selectinload(RequestMember.member),
                selectinload(RequestMember.community),
                selectinload(RequestMember.status),
            )
            .where(RequestMember.id == request_member_id)
        )
        return await self._session.scalar(query)

    async def _create_child_request_members(
            self, community_id: str, user_settings_id: str) -> None:
        query = (
            select(RequestMember)
            .options(
                selectinload(RequestMember.member),
                selectinload(RequestMember.community),
                selectinload(RequestMember.status),
            )
            .where(
                RequestMember.community_id == community_id,
                RequestMember.parent_id is None,
            )
        )
        request_members = await self._session.scalars(query)

        data_to_add: List[RelationRow] = []
        for request_member in list(request_members):
            child_request_member = self._create_copy_request_member(request_member)
            child_request_member.parent_id = request_member.id
            status = await self._get_status_by_code('voted_by_default')
            child_request_member.status = status
            try:
                self._session.add(child_request_member)
            except Exception as e:
                logger.error(f'Дочерний запрос на добавление члена сообщества '
                             f'(родителя с id {request_member.id}) не может быть создан: {e}')
                continue

            data_to_add.append(
                RelationRow(
                    id=build_uuid(),
                    from_id=user_settings_id,
                    to_id=child_request_member.id,
                )
            )
        if data_to_add:
            stmt: Insert = insert(RelationUserCsRequestMember).values(*data_to_add)
            stmt.compile()
            await self._session.execute(stmt)

    async def _get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    @staticmethod
    def _create_copy_request_member(request_member: RequestMember) -> RequestMember:
        new_request_member = RequestMember()
        new_request_member.id = build_uuid()
        for key, value in request_member.__dict__.items():
            if RequestMember.__annotations__.get(key):
                setattr(new_request_member, key, value)

        return new_request_member