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
from entities.status.model import Status

logger = logging.getLogger(__name__)


class UserCommunitySettingsDS(CRUDDataStorage[RequestMember]):

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
        parent_status_query = (
            select(Status)
            .where(Status.code == 'community_member')
        )
        parent_status = await self._session.scalar(parent_status_query)
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
            status_query = (
                select(Status)
                .where(Status.code == 'voted_by_default')
            )
            status = await self._session.scalar(status_query)
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

    @staticmethod
    def _create_copy_request_member(request_member: RequestMember) -> RequestMember:
        new_request_member = RequestMember()
        new_request_member.id = build_uuid()
        for key, value in request_member.__dict__.items():
            if RequestMember.__annotations__.get(key):
                setattr(new_request_member, key, value)

        return new_request_member
