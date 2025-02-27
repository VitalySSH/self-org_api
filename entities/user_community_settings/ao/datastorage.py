import logging
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth.models.user import User
from datastorage.ao.base import AODataStorage
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import RequestMember
from datastorage.utils import build_uuid
from entities.community.model import Community
from entities.community_description.model import CommunityDescription
from entities.community_name.model import CommunityName
from entities.community_settings.model import CommunitySettings
from entities.category.model import Category
from entities.status.model import Status
from entities.user_community_settings.ao.dataclasses import CreatingCommunity
from entities.user_community_settings.model import UserCommunitySettings

logger = logging.getLogger(__name__)


class UserCommunitySettingsDS(
    AODataStorage[UserCommunitySettings],
    CRUDDataStorage
):

    _model = UserCommunitySettings

    async def create_community(
            self, data_to_create: CreatingCommunity
    ) -> None:
        """Создание нового сообщества
        на основе пользовательских настроек.
        """
        data_to_create.community_id = build_uuid()
        await self._create_community_name(data_to_create)
        await self._create_community_description(data_to_create)
        await self._create_categories(
            data_to_create=data_to_create, is_selected=True)
        user_settings = await self._create_user_settings(data_to_create)
        main_settings = await self._create_main_settings(data_to_create)

        community = Community()
        community.id = data_to_create.community_id
        community.main_settings = main_settings
        community.user_settings.append(user_settings)
        community.creator = data_to_create.user

        self._session.add(community)
        await self._session.flush([community])
        await self._session.refresh(community)

        request_member = await self._create_request_member(
            community=community, user=data_to_create.user)
        main_settings.adding_members.append(request_member)
        child_request_member = await self._create_child_request_member(
            community=community,
            user=data_to_create.user,
            request_member=request_member
        )
        user_settings.adding_members.append(child_request_member)
        await self._session.commit()

    async def create_child_settings(
            self, data_to_create: CreatingCommunity
    ) -> UserCommunitySettings:
        """Создание пользовательских настроек для внутренних сообществ."""
        data_to_create.community_id = build_uuid()
        await self._create_community_name(data_to_create)
        await self._create_community_description(data_to_create)
        await self._create_categories(data_to_create=data_to_create)
        settings = await self._create_user_settings(data_to_create)
        await self._session.commit()

        return settings

    async def get_or_create_child_community(
            self, user_settings: UserCommunitySettings
    ) -> Community:
        """Создание внутреннего сообщества, если оно отсутствует
        на основе утверждённых большинством пользовательских настроек.
        """
        community = await self.get_community(user_settings.community_id)
        if community:
            return community

        main_settings = await self._create_child_main_settings(user_settings)
        community = Community()
        community.id = user_settings.community_id
        community.main_settings = main_settings
        community.user_settings.append(user_settings)
        community.creator = user_settings.user
        parent_community_id: Optional[str] = user_settings.parent_community_id
        if parent_community_id:
            community.parent = await self._session.get(
                Community, parent_community_id)
        self._session.add(community)
        await self._session.flush([community])
        await self._session.refresh(community)

        request_member = await self._create_request_member(
            community=community, user=user_settings.user)
        main_settings.adding_members.append(request_member)
        child_request_member = await self._create_child_request_member(
            community=community,
            user=user_settings.user,
            request_member=request_member
        )
        user_settings.adding_members.append(child_request_member)

        return community

    async def _create_community_name(
            self, data_to_create: CreatingCommunity
    ) -> None:
        community_name = CommunityName()
        community_name.name = data_to_create.name
        community_name.community_id = data_to_create.community_id
        community_name.creator_id = data_to_create.user.id
        community_name.is_readonly = True
        self._session.add(community_name)
        await self._session.flush([community_name])
        data_to_create.name_obj = community_name

    async def _create_community_description(
            self, data_to_create: CreatingCommunity
    ) -> None:
        description = CommunityDescription()
        description.value = data_to_create.description
        description.community_id = data_to_create.community_id
        description.creator_id = data_to_create.user.id
        description.is_readonly = True
        self._session.add(description)
        await self._session.flush([description])
        data_to_create.description_obj = description

    async def _create_categories(
            self, data_to_create: CreatingCommunity,
            is_selected: bool = False,
    ) -> None:
        categories: List[Category] = []
        category_names = data_to_create.category_names
        status_code = (Code.CATEGORY_SELECTED if
                       is_selected else Code.ON_CONSIDERATION)
        category_status: Status = await self.get_status_by_code(status_code)
        for category_name in category_names:
            category = Category()
            category.name = category_name
            category.community_id = data_to_create.community_id
            category.creator_id = data_to_create.user.id
            category.status = category_status
            self._session.add(category)
            await self._session.flush([category])
            await self._session.refresh(category)
            categories.append(category)

        data_to_create.categories_objs = categories

    async def _create_system_category(
            self, community_id:
            str, creator_id: str
    ) -> Category:
        category_status = await self.get_status_by_code(Code.SYSTEM_CATEGORY)
        category = Category()
        category.name = 'Общие вопросы'
        category.community_id = community_id
        category.creator_id = creator_id
        category.status = category_status
        self._session.add(category)
        await self._session.flush([category])
        await self._session.refresh(category)

        return category

    async def _create_main_settings(
            self, data_to_create: CreatingCommunity
    ) -> CommunitySettings:
        settings = CommunitySettings()
        settings.name = data_to_create.name_obj
        settings.description = data_to_create.description_obj
        settings.quorum = data_to_create.settings.get('quorum')
        settings.vote = data_to_create.settings.get('vote')
        settings.significant_minority = (
            data_to_create.settings.get('significant_minority')
        )
        settings.is_secret_ballot = (
            data_to_create.settings.get('is_secret_ballot')
        )
        settings.is_can_offer = data_to_create.settings.get('is_can_offer')
        settings.is_minority_not_participate = data_to_create.settings.get(
            'is_minority_not_participate')
        system_category = await self._create_system_category(
            community_id=data_to_create.community_id,
            creator_id=data_to_create.user.id
        )
        categories = [system_category]
        categories += data_to_create.categories_objs
        settings.categories = categories
        self._session.add(settings)
        await self._session.flush([settings])
        await self._session.refresh(settings)

        return settings

    async def _create_child_main_settings(
            self, user_settings: UserCommunitySettings
    ) -> CommunitySettings:
        settings = CommunitySettings()
        settings.name = user_settings.name
        settings.description = user_settings.description
        settings.quorum = user_settings.quorum
        settings.vote = user_settings.vote
        settings.significant_minority = user_settings.significant_minority
        settings.is_secret_ballot = user_settings.is_secret_ballot
        settings.is_can_offer = user_settings.is_can_offer
        settings.is_minority_not_participate = (
            user_settings.is_minority_not_participate
        )
        settings.categories = user_settings.categories
        self._session.add(settings)
        await self._session.flush([settings])
        await self._session.refresh(settings)

        return settings

    async def _create_user_settings(
            self, data_to_create: CreatingCommunity,
    ) -> UserCommunitySettings:
        """Создание пользовательских настроек."""
        settings = UserCommunitySettings()
        settings.user = data_to_create.user
        settings.community_id = data_to_create.community_id
        settings.name = data_to_create.name_obj
        settings.description = data_to_create.description_obj
        settings.quorum = data_to_create.settings.get('quorum')
        settings.vote = data_to_create.settings.get('vote')
        settings.significant_minority = (
            data_to_create.settings.get('significant_minority')
        )
        settings.is_secret_ballot = (
            data_to_create.settings.get('is_secret_ballot')
        )
        settings.is_can_offer = data_to_create.settings.get('is_can_offer')
        settings.is_minority_not_participate = (
            data_to_create.settings.get('is_minority_not_participate')
        )
        settings.is_not_delegate = (
            data_to_create.settings.get('is_not_delegate')
        )
        settings.is_default_add_member = (
            data_to_create.settings.get('is_default_add_member')
        )
        settings.categories = data_to_create.categories_objs
        if data_to_create.parent_community_id:
            settings.parent_community_id = data_to_create.parent_community_id
        self._session.add(settings)
        await self._session.flush([settings])
        await self._session.refresh(settings)

        return settings

    async def _create_request_member(
            self, community: Community, user: User
    ) -> RequestMember:
        request_member = RequestMember()
        request_member.member = user
        request_member.community = community
        request_member.status = (
            await self.get_status_by_code(Code.COMMUNITY_MEMBER)
        )
        request_member.vote = True
        request_member.reason = 'Инициатор создания сообщества'
        self._session.add(request_member)
        await self._session.flush([request_member])

        return request_member

    async def _create_child_request_member(
            self, community: Community,
            user: User,
            request_member: RequestMember
    ) -> RequestMember:
        child_request_member = self._create_copy_request_member(request_member)
        child_request_member.parent_id = request_member.id
        status = await self.get_status_by_code(Code.VOTED)
        child_request_member.community = community
        child_request_member.member = user
        child_request_member.status = status
        self._session.add(child_request_member)
        await self._session.flush([child_request_member])

        return child_request_member

    async def get_community(self, community_id: str) -> Optional[Community]:
        query = select(Community).where(Community.id == community_id)

        return await self._session.scalar(query)

    async def _get_request_member(
            self, request_member_id: str
    ) -> Optional[RequestMember]:
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

    @staticmethod
    def _create_copy_request_member(
            request_member: RequestMember
    ) -> RequestMember:
        new_request_member = RequestMember()
        new_request_member.id = build_uuid()
        for key, value in request_member.__dict__.items():
            if RequestMember.__annotations__.get(key):
                if key == 'id':
                    continue
                setattr(new_request_member, key, value)

        return new_request_member
