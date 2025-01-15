import logging
from datetime import datetime
from typing import Optional, List, cast, Sequence

from sqlalchemy import select, insert, func, Insert, Row
from sqlalchemy.orm import selectinload

from auth.models.user import User
from core.dataclasses import BaseVotingParams, PercentByName
from datastorage.ao.base import AODataStorage
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import (
    RequestMember, CommunitySettings, RelationUserCsRequestMember, UserCommunitySettings
)
from datastorage.decorators import ds_async_with_new_session
from datastorage.interfaces import RelationRow
from datastorage.utils import build_uuid
from entities.community.model import Community
from entities.status.model import Status

logger = logging.getLogger(__name__)


class RequestMemberDS(AODataStorage[RequestMember], CRUDDataStorage):

    _model = RequestMember

    async def get_request_member_in_percent(self, request_member_id: str) -> List[PercentByName]:
        """Вернёт статистику по голосам запроса на членство в сообществе."""
        child_request_members = await self._get_child_request_members(
            request_member_id=request_member_id)
        total_count: int = len(child_request_members)
        allowed_count: int = len(list(filter(lambda it: it.vote is True, child_request_members)))
        banned_count: int = len(list(filter(lambda it: it.vote is False, child_request_members)))
        abstain: int = total_count - (allowed_count + banned_count)

        return [
            PercentByName(name='За', percent=int(allowed_count / total_count * 100)),
            PercentByName(name='Против', percent=int(banned_count / total_count * 100)),
            PercentByName(name='Воздержалось', percent=int(abstain / total_count * 100)),
        ]

    @ds_async_with_new_session
    async def add_request_member_to_settings(self, request_member_id: str) -> None:
        """Обновление данных после создания
        основного запроса на добавление в сообщество.

        Добавление основного запроса в настройки сообщества.
        Создание и добавление дочерних запросов в пользовательские настройки.
        Пересчёт голосов по дочерним запросам.
        """
        request_member: Optional[RequestMember] = await self._get_request_member(request_member_id)
        if not request_member:
            return

        if request_member.parent_id:
            parent_request_member: Optional[RequestMember] = await self._get_request_member(
                cast(str, request_member.parent_id))
            await self._update_vote_in_parent_requests_member(parent_request_member)
        else:
            await self._add_request_member_to_settings(request_member)
            await self._update_vote_in_parent_requests_member(request_member)

        await self._session.commit()

    @ds_async_with_new_session
    async def update_parent_request_member(self, request_member_id: str) -> None:
        """Обновление состояния основного запроса
         на добавление в сообщество, после изменений голосов дочерних запросов.
         """
        request_member: Optional[RequestMember] = await self._get_request_member(request_member_id)
        if request_member and request_member.parent_id:
            parent_request_member: Optional[RequestMember] = await self._get_request_member(
                request_member.parent_id)
            if parent_request_member:
                await self._update_vote_in_parent_requests_member(parent_request_member)
                await self._session.commit()

    @ds_async_with_new_session
    async def delete_child_request_members(self, request_member_id: str) -> None:
        """Удаление дочерних запросов на добавление
         в сообщество, после удаления основного.
         """
        is_deleted: bool = await self._delete_child_request_members(request_member_id)
        if is_deleted:
            await self._session.commit()

    async def add_new_member(self, request_member_id: str, current_user: User) -> None:
        """Добавление нового члена сообщества по утверждённой заявке.

        Добавление пользовательских настроек в сообщество.
        Обновление статуса основного запроса на добавление в сообщество.
        Создание пользовательских запросов
        на членство остальных участников сообщества.
        """
        request_member: RequestMember = await self.get(
            instance_id=request_member_id,
            include=[
                'member',
                'community.user_settings',
                'community.main_settings.name',
                'community.main_settings.description',
                'community.main_settings.categories',
            ]
        )
        community: Community = request_member.community
        user_settings = await self._create_user_settings(
            community=community, current_user=current_user)
        community.user_settings.append(user_settings)
        await self._update_parent_request_member(request_member)
        await self._create_child_request_members(
            parent_request_member=request_member, user_settings_id=user_settings.id)
        await self._session.commit()

    async def _delete_child_request_members(self, request_member_id: str) -> bool:
        is_deleted = False
        community_id, user_id = None, None
        child_request_members = await self._get_child_request_members(
            request_member_id=request_member_id, is_active=False)

        for child_request_member in child_request_members:
            if not community_id:
                community_id = child_request_member.community_id
            if not user_id:
                user_id = child_request_member.member_id

            _is_deleted = await self._delete_request_member(child_request_member)
            if not is_deleted and _is_deleted:
                is_deleted = True

        if community_id and user_id:
            _is_deleted: bool = await self._check_and_delete_user_settings(
                community_id=community_id, user_id=user_id)
            if not is_deleted and _is_deleted:
                is_deleted = True

            child_community_id: Optional[str] = await self._get_child_community_id(community_id)
            if child_community_id:
                child_request_member = await self._get_child_request_member(
                    community_id=child_community_id, user_id=user_id)
                if child_request_member:
                    child_request_member_id = child_request_member.id
                    _is_deleted = await self._delete_request_member(child_request_member)
                    if not is_deleted and _is_deleted:
                        is_deleted = True

                    _is_deleted = await self._delete_child_request_members(child_request_member_id)
                    if not is_deleted and _is_deleted:
                        is_deleted = True

        return is_deleted

    async def _delete_request_member(self, request_member) -> bool:
        try:
            await self._session.delete(request_member)
            return True
        except Exception as e:
            logger.error(f'Не удалось удались запрос на членство '
                         f'с id: {request_member.id}: {e}')
            return False

    async def _create_user_settings(
            self, community: Community, current_user: User) -> UserCommunitySettings:
        user_settings = UserCommunitySettings()
        user_settings.user = current_user
        user_settings.community_id = community.id
        user_settings.name = community.main_settings.name
        user_settings.description = community.main_settings.description
        user_settings.quorum = community.main_settings.quorum
        user_settings.vote = community.main_settings.vote
        user_settings.significant_minority = community.main_settings.significant_minority
        user_settings.is_secret_ballot = community.main_settings.is_secret_ballot
        user_settings.is_can_offer = community.main_settings.is_can_offer
        user_settings.is_minority_not_participate = (
            community.main_settings.is_minority_not_participate
        )
        user_settings.categories = community.main_settings.categories
        user_settings.is_not_delegate = False
        user_settings.is_default_add_member = False
        try:
            self._session.add(user_settings)
            await self._session.flush([user_settings])
            await self._session.refresh(user_settings)
        except Exception as e:
            raise Exception(f'Не удалось создать пользовательские настройки: {e}')

        return user_settings

    async def _update_parent_request_member(self, request_member: RequestMember) -> None:
        request_member.status = await self._get_status_by_code(Code.COMMUNITY_MEMBER)
        request_member.updated = datetime.now()
        await self._session.flush([request_member])

    async def _create_child_request_members(
            self, parent_request_member: RequestMember, user_settings_id: str) -> None:
        query = (
            select(RequestMember)
            .options(
                selectinload(RequestMember.member),
                selectinload(RequestMember.community),
                selectinload(RequestMember.status),
            )
            .where(
                RequestMember.community_id == parent_request_member.community_id,
                RequestMember.parent_id.is_(None),
            )
        )
        request_members = await self._session.scalars(query)

        data_to_add: List[RelationRow] = []
        for request_member in list(request_members):
            child_request_member: RequestMember = self._create_copy_request_member(request_member)
            child_request_member.parent_id = request_member.id
            if request_member.id == parent_request_member.id:
                status: Status = await self._get_status_by_code(Code.VOTED)
            else:
                status: Status = await self._get_status_by_code(Code.VOTED_BY_DEFAULT)
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
            stmt: Insert = insert(RelationUserCsRequestMember).values(data_to_add)
            stmt.compile()
            await self._session.execute(stmt)

    async def _check_and_delete_user_settings(self, community_id: str, user_id: str) -> bool:
        is_deleted = False
        query = (
            select(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.user_id == user_id,
            )
        )
        user_settings = await self._session.scalar(query)
        if user_settings:
            try:
                await self._session.delete(user_settings)
                if not is_deleted:
                    is_deleted = True
            except Exception as e:
                logger.error(f'Не удалось удались пользовательские настройки сообщества '
                             f'с id: {user_settings.id}: {e}')

        return is_deleted

    async def _add_request_member_to_settings(self, request_member: RequestMember) -> None:
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

    async def _get_child_community_id(self, community_id: str) -> Optional[str]:
        query = select(Community.parent_id).where(Community.id == community_id)
        result = await self._session.execute(query)
        row = result.fetchone()

        return row[0] if row else None

    async def _get_child_request_members(
            self, request_member_id: str, is_active: bool = True) -> List[RequestMember]:
        filters = [RequestMember.parent_id == request_member_id]
        if is_active:
            filters.append(RequestMember.is_blocked.is_not(True))
        query = select(RequestMember).where(*filters)
        child_request_members = await self._session.scalars(query)

        return list(child_request_members)

    async def _get_child_request_member(
            self, community_id: str, user_id: str) -> Optional[RequestMember]:
        query = select(RequestMember).where(
            RequestMember.community_id == community_id,
            RequestMember.member_id == user_id,
            RequestMember.parent_id.is_(None),
        )

        return await self._session.scalar(query)

    async def _add_rm_to_user_community_settings(self, request_member: RequestMember) -> None:
        """Добавление дочерних запросов на членство в
        пользовательские настройки после создания основного запроса.
        """
        user_cs_query = (
            select(
                UserCommunitySettings.id,
                UserCommunitySettings.is_default_add_member,
                UserCommunitySettings.user_id,
                UserCommunitySettings.is_blocked,
            ).where(UserCommunitySettings.community_id == request_member.community_id)
        )
        user_cs_data = await self._session.execute(user_cs_query)
        user_cs_list = user_cs_data.all()

        data_to_add: List[RelationRow] = []
        for id_, is_default_add_member, user_id, is_blocked in user_cs_list:
            child_request_member = self._create_copy_request_member(request_member)
            child_request_member.parent_id = request_member.id
            if is_default_add_member or request_member.member.id == user_id:
                status_query = select(Status).where(Status.code == Code.VOTED)
                status = await self._session.scalar(status_query)
                child_request_member.vote = True
                child_request_member.status = status
            if is_blocked:
                child_request_member.is_blocked = True
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
            stmt: Insert = insert(RelationUserCsRequestMember).values(data_to_add)
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

    async def _update_vote_in_parent_requests_member(self, request_member: RequestMember) -> None:
        """Обновление состояния основного запроса на членство
        через пересчёт голосов по дочерним запросам.
        """
        last_vote: bool = request_member.vote
        last_status: Status = request_member.status
        voting_params: BaseVotingParams = await self.calculate_voting_params(
            request_member.community_id)
        voted: Sequence[Row] = await self._get_voted_by_requests_member(request_member)
        users_count: int = await self._get_count_users_in_community(request_member.community_id)
        len_voted = len(voted)
        voted_count = int(len_voted / users_count * 100) if len_voted > 0 else 0
        if voted_count >= voting_params.quorum:
            allowed_count: int = len(list(filter(lambda it: it[0] is True, voted)))
            percentage_yes = int(allowed_count / len_voted * 100)
            percentage_no: int = 100 - percentage_yes
            if voting_params.vote <= percentage_yes:
                request_member.vote = True
            elif voting_params.vote <= percentage_no:
                request_member.vote = False

            if last_vote and not request_member.vote:
                if last_status.code == Code.COMMUNITY_MEMBER:
                    request_member.status = await self._get_status_by_code(Code.MEMBER_EXCLUDED)
                    await self._block_user_settings(request_member)
                elif last_status.code == Code.REQUEST_SUCCESSFUL:
                    request_member.status = await self._get_status_by_code(Code.REQUEST_DENIED)
            elif not last_vote and request_member.vote:
                if last_status.code == Code.ON_CONSIDERATION:
                    request_member.status = await self._get_status_by_code(Code.REQUEST_SUCCESSFUL)
                elif last_status.code == Code.MEMBER_EXCLUDED:
                    request_member.status = await self._get_status_by_code(Code.COMMUNITY_MEMBER)
                    await self._unblock_user_settings(request_member)
                elif last_status.code == Code.REQUEST_DENIED:
                    request_member.status = await self._get_status_by_code(Code.REQUEST_SUCCESSFUL)

    async def _get_voted_by_requests_member(self, request_member: RequestMember) -> Sequence[Row]:
        query = (
            select(RequestMember.vote)
            .where(
                RequestMember.vote.is_not(None),
                RequestMember.is_blocked.is_not(True),
                RequestMember.community_id == request_member.community_id,
                RequestMember.member_id == request_member.member_id,
                RequestMember.parent_id.is_not(None),
            )
        )
        voted_data = await self._session.execute(query)

        return voted_data.all()

    async def _block_user_settings(self, request_member: RequestMember) -> None:
        query = (
            select(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == request_member.community_id,
                UserCommunitySettings.user_id == request_member.member_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        user_settings = await self._session.scalar(query)
        if user_settings:
            user_settings.is_blocked = True

    async def _unblock_user_settings(self, request_member: RequestMember) -> None:
        query = (
            select(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == request_member.community_id,
                UserCommunitySettings.user_id == request_member.member_id,
                UserCommunitySettings.is_blocked.is_(True),
            )
        )
        user_settings = await self._session.scalar(query)
        if user_settings:
            user_settings.is_blocked = False

    async def _get_count_users_in_community(self, community_id: str) -> int:
        query = (
            select(func.count()).select_from(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id == community_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        row = await self._session.scalar(query)

        return int(row) if row else 0

    async def _get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)
