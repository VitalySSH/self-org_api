import logging
from typing import Optional, List

from sqlalchemy import select, insert, func, Insert
from sqlalchemy.orm import selectinload

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import (
    RequestMember, CommunitySettings, RelationUserCsRequestMember, UserCommunitySettings
)
from datastorage.decorators import ds_async_with_new_session
from datastorage.interfaces import RelationRow
from datastorage.utils import build_uuid
from entities.status.model import Status

logger = logging.getLogger(__name__)


class RequestMemberDS(CRUDDataStorage[RequestMember]):

    @ds_async_with_new_session
    async def add_request_member(self, request_member_id: str) -> None:
        request_member = await self._get_request_member(request_member_id)
        if not request_member:
            return
        if request_member.parent_id:
            await self._update_vote_for_requests_member(request_member)
        else:
            await self._add_request_member(request_member)

    async def _add_request_member(self, request_member: RequestMember) -> None:
        main_settings_id = (request_member.community.main_settings_id if
                            request_member.community else None)
        if main_settings_id:
            query = (
                select(CommunitySettings)
                .options(selectinload(CommunitySettings.adding_members))
                .where(CommunitySettings.id == main_settings_id)
            )
            main_settings = await self._session.scalar(query)

            if main_settings and isinstance(main_settings.adding_members, list):
                filtered = list(filter(lambda it: it.id == request_member.id,
                                       main_settings.adding_members))
                if not filtered:
                    main_settings.adding_members.append(request_member)

            await self._add_rm_to_user_community_settings(request_member)
            await self._session.commit()

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

    async def _add_rm_to_user_community_settings(self, request_member: RequestMember) -> None:
        user_cs_query = (
            select(
                UserCommunitySettings.id,
                UserCommunitySettings.is_default_add_member,
                UserCommunitySettings.user_id,
            ).where(UserCommunitySettings.community_id == request_member.community_id)
        )
        user_cs_data = await self._session.execute(user_cs_query)
        user_cs_list = user_cs_data.all()

        data_to_add: List[RelationRow] = []
        for id_, is_default_add_member, user_id in user_cs_list:
            child_request_member = self._create_copy_request_member(request_member)
            child_request_member.parent_id = request_member.id
            if is_default_add_member or request_member.member.id == user_id:
                status_query = (
                    select(Status)
                    .where(Status.code == 'voted')
                )
                status = await self._session.scalar(status_query)
                child_request_member.vote = True
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
                    from_id=id_,
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

    async def _update_vote_for_requests_member(self, request_member: RequestMember) -> None:
        query = (
            select(func.count()).select_from(RequestMember)
            .where(
                RequestMember.vote.is_(True),
                RequestMember.community_id == request_member.community_id,
            )
        )
        allowed_count = await self._session.scalar(query)
        vote_count = await self._count_votes_by_settings(request_member.community_id)
        parent_request_member = await self._get_request_member(request_member.community_id)
        if vote_count and vote_count <= allowed_count:
            parent_request_member.vote = True
        else:
            parent_request_member.vote = False

        await self._session.commit()

    async def _count_votes_by_settings(self, community_id: str) -> int:
        query = (
            select(func.avg(UserCommunitySettings.vote))
            .select_from(UserCommunitySettings)
            .where(UserCommunitySettings.community_id == community_id)
        )
        row = await self._session.scalar(query)

        return int(row) if row else 0
