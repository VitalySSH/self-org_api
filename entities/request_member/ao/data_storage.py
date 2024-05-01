import logging
from copy import deepcopy
from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload

from datastorage.base import DataStorage
from datastorage.database.models import (
    RequestMember, CommunitySettings, Community, RelationUserCsRequestMember,
    UserCommunitySettings
)
from datastorage.decorators import ds_async_with_new_session
from datastorage.utils import build_uuid

logger = logging.getLogger(__name__)


class RequestMemberDS(DataStorage[RequestMember]):

    @ds_async_with_new_session
    async def add_request_member(self, request_member_id: str) -> None:
        request_member = await self._get_request_member(request_member_id)
        if not request_member:
            return
        if request_member.is_removal:
            return
        await self._add_request_member(request_member)

    async def _add_request_member(self, request_member: RequestMember) -> None:
        if request_member.is_removal:
            return None
        community_query = (
            select(Community)
            .options(selectinload(Community.main_settings)
                     .options(selectinload(CommunitySettings.adding_members)))
            .where(Community.id == request_member.community_id)
        )
        community = await self._session.scalar(community_query)
        if not community:
            logger.error(f'ERROR POSTPROCESSING REQUEST MEMBER: '
                         f'не найдено сообщество с id {request_member.community_id}')
            return

        community_settings = community.main_settings
        (community_settings.adding_members or []).append(request_member)

        await self._add_rm_to_user_community_settings(request_member)
        await self._session.commit()

    async def _get_request_member(self, request_member_id: str) -> Optional[RequestMember]:
        query = (
            select(RequestMember)
            .where(RequestMember.id == request_member_id)
        )
        return await self._session.scalar(query)

    async def _add_rm_to_user_community_settings(self, request_member: RequestMember) -> None:
        user_cs_query = (
            select(UserCommunitySettings.id, UserCommunitySettings.is_default_add_member)
            .where(UserCommunitySettings.community_id == request_member.community_id)
        )
        user_cs_data = await self._session.scalars(user_cs_query)
        user_cs_list = list(user_cs_data)

        data_to_add = []
        for user_cs in user_cs_list:
            child_request_member = deepcopy(request_member)
            child_request_member.id = build_uuid()
            child_request_member.parent_id = request_member.id
            if user_cs.is_default_add_member:
                child_request_member.vote = True
            try:
                self._session.add(child_request_member)
                await self._session.flush()
            except Exception as e:
                logger.error(f'Дочерний запрос на добавление члена сообщества '
                             f'(родителя с id {request_member.id}) не может быть создан: {e}')
                continue

            data_to_add.append(
                {
                    'id': build_uuid(),
                    'from_id': user_cs.id,
                    'to_id': child_request_member.id,
                }
            )

        stmt = insert(RelationUserCsRequestMember).values(*data_to_add)
        stmt.compile()

