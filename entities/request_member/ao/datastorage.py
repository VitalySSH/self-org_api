import logging
from datetime import datetime
from typing import Optional, List, cast, Dict, Set, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

from auth.models.user import User
from core.dataclasses import PercentByName, SimpleVoteResult
from datastorage.ao.datastorage import AODataStorage
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.list import Filters, Filter, Operation
from datastorage.database.models import (
    RequestMember, CommunitySettings, UserCommunitySettings
)
from datastorage.utils import build_uuid
from entities.community.model import Community
from entities.request_member.ao.dataclasses import MyMemberRequest
from entities.status.model import Status
from entities.user_voting_result.model import UserVotingResult
from entities.voting_option.model import VotingOption
from entities.voting_result.model import VotingResult

logger = logging.getLogger(__name__)


class RequestMemberDS(
    AODataStorage[RequestMember],
    CRUDDataStorage[RequestMember],
):
    _model = RequestMember

    async def get_request_member_in_percent(
            self, request_member_id: str
    ) -> List[PercentByName]:
        """Вернёт статистику по голосам запроса на членство в сообществе."""
        request_member = await self._get_request_member(
            request_member_id=request_member_id,
            with_options=False,
        )
        vote_in_percent: SimpleVoteResult = (
            await self.get_vote_stats_by_requests_member(request_member)
        )

        return [
            PercentByName(name='За', percent=vote_in_percent.yes),
            PercentByName(name='Против', percent=vote_in_percent.no),
            PercentByName(name='Воздержалось',
                          percent=vote_in_percent.abstain),
        ]

    async def update_request_member_data(
            self,
            request_member_id: str,
    ) -> None:
        """Обновление данных после создания
        основного запроса на добавление в сообщество.

        Создание дочерних запросов.
        Пересчёт голосов по дочерним запросам.
        """
        async with self.session_scope():
            request_member = await self._get_request_member(
                request_member_id=request_member_id,
            )
            if not request_member:
                return

            if request_member.parent_id:
                parent_request_member = await self._get_request_member(
                    request_member_id=cast(str, request_member.parent_id)
                )
                await self.update_vote_in_parent_requests_member(
                    parent_request_member
                )
            else:
                await self._create_child_request_members_after_main(
                    request_member
                )
                await self.update_vote_in_parent_requests_member(
                    request_member
                )

    async def update_parent_request_member(
            self,
            request_member_id: str
    ) -> None:
        """Обновление состояния основного запроса
         на добавление в сообщество, после изменений голосов дочерних запросов.
         """
        async with self.session_scope():
            request_member = await self._get_request_member(
                request_member_id=request_member_id,
                with_options=False
            )
            if request_member and request_member.parent_id:
                parent_request_member = await self._get_request_member(
                    request_member_id=cast(str, request_member.parent_id)
                )
                if parent_request_member:
                    await self.update_vote_in_parent_requests_member(
                        parent_request_member
                    )

    async def delete_child_request_members(
            self, request_member_id: str
    ) -> None:
        """Удаление дочерних запросов на добавление
         в сообщество, после удаления основного.
         """
        async with self.session_scope():
            await self._delete_child_request_members(request_member_id)

    async def add_new_member(
            self,
            request_member_id: str,
            current_user: User
    ) -> None:
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
                'community.main_settings.categories.status',
                'community.main_settings.sub_communities_settings',
            ]
        )
        community: Community = request_member.community
        user_settings, is_new = await self._create_user_settings(
            community=community, current_user=current_user
        )
        if is_new:
            community.user_settings.append(user_settings)
        await self._update_parent_request_member(request_member)
        await self._create_child_request_members(request_member)
        await self._create_new_voting_results(request_member)

    async def my_list(self, member_id: str) -> List[MyMemberRequest]:
        """Вернёт список заявок на добавление
        в сообщества для текущего пользователя.
        """
        stmt = (
            select(self._model)
            .where(
                self._model.member_id == member_id,
                self._model.parent_id.is_(None),
            )
            .options(
                joinedload(self._model.status),
                joinedload(self._model.community)
                .joinedload(Community.main_settings)
                .joinedload(CommunitySettings.name),
                joinedload(self._model.community)
                .joinedload(Community.main_settings)
                .joinedload(CommunitySettings.description),
                joinedload(self._model.community)
                .joinedload(Community.parent),
            )
        )

        result = await self._session.execute(stmt)
        request_members: List[RequestMember] = list(result.scalars())

        all_requests: Dict[str, MyMemberRequest] = {}
        communities_in_requests: Set[str] = set()

        for req in request_members:
            community: Community = req.community
            settings: Optional[CommunitySettings] = community.main_settings

            # FIXME: разобраться, почему иногда не срабатывает joinedload
            if settings is None and community.main_settings_id:
                settings = await self.get(
                    instance_id=community.main_settings_id,
                    include=['name', 'description'],
                    model=CommunitySettings,
                )

            req_data = MyMemberRequest(
                key=req.id,
                communityId=community.id,
                communityName=settings.name.name,
                communityDescription=settings.description.value,
                status=req.status.name,
                statusCode=req.status.code,
                reason=req.reason,
                created=req.created.strftime('%d.%m.%Y %H:%M'),
                children=[],
            )

            all_requests[community.id] = req_data
            communities_in_requests.add(community.id)

            if community.parent_id:
                communities_in_requests.add(community.parent_id)

        root_requests: List[MyMemberRequest] = []

        for req in request_members:
            community: Community = req.community
            req_data: MyMemberRequest = all_requests[community.id]

            if (not community.parent_id or
                    community.parent_id not in all_requests):
                root_requests.append(req_data)

        for req in request_members:
            community: Community = req.community
            if community.parent_id and community.parent_id in all_requests:
                parent_data: MyMemberRequest = all_requests[
                    community.parent_id
                ]
                parent_data['children'].append(all_requests[community.id])

        def sort_key(r_: MyMemberRequest) -> tuple:
            """Ключ для сортировки:
            сначала корневые, затем по дате (новые выше).
            """
            try:
                dt = datetime.strptime(
                    r_.get('created'), '%d.%m.%Y %H:%M'
                )
                return (
                    0 if not r_.get('children') else 1,
                    -dt.timestamp()
                )
            except ValueError:
                return 0, 0

        root_requests.sort(key=sort_key)
        for r in root_requests:
            if r.get('children'):
                r['children'].sort(key=sort_key)

        return root_requests

    async def _delete_child_request_members(
            self, request_member_id: str
    ) -> None:
        community_id, user_id = None, None
        child_request_members = await self._get_child_request_members(
            request_member_id
        )

        for child_request_member in child_request_members:
            if not community_id:
                community_id = child_request_member.community_id
            if not user_id:
                user_id = child_request_member.member_id

            await self._delete_request_member(child_request_member)

        if community_id and user_id:
            await self._check_and_delete_user_settings(
                community_id=community_id, user_id=user_id
            )

            child_community_id = await self._get_child_community_id(
                community_id
            )
            if child_community_id:
                child_request_member = await self._get_child_request_member(
                    community_id=child_community_id,
                    user_id=user_id
                )
                if child_request_member:
                    child_request_member_id = child_request_member.id
                    await self._delete_request_member(child_request_member)
                    await self._delete_child_request_members(
                        child_request_member_id
                    )

        await self._delete_user_voting_results(user_id)

    async def _delete_request_member(self, request_member) -> None:
        try:
            await self._session.delete(request_member)
        except Exception as e:
            logger.error(f'Не удалось удались запрос на членство '
                         f'с id: {request_member.id}: {e.__str__()}')

    async def _create_user_settings(
            self, community: Community,
            current_user: User
    ) -> Tuple[UserCommunitySettings, bool]:
        filters: Filters = [
            Filter(field='community_id', op=Operation.EQ, val=community.id),
            Filter(field='user_id', op=Operation.EQ, val=current_user.id),
        ]
        current_user_settings = await self.list(
            filters=filters, model=UserCommunitySettings
        )
        if current_user_settings.total:
            return current_user_settings.data[0], False

        user_settings = UserCommunitySettings()
        user_settings.user = current_user
        user_settings.community_id = community.id
        user_settings.names = [community.main_settings.name]
        user_settings.descriptions = [community.main_settings.description]
        user_settings.quorum = community.main_settings.quorum
        user_settings.vote = community.main_settings.vote
        user_settings.significant_minority = (
            community.main_settings.significant_minority
        )
        user_settings.decision_delay = community.main_settings.decision_delay
        user_settings.dispute_time_limit = (
            community.main_settings.dispute_time_limit
        )
        user_settings.is_workgroup = community.main_settings.is_workgroup
        user_settings.workgroup = community.main_settings.workgroup
        user_settings.is_secret_ballot = (
            community.main_settings.is_secret_ballot
        )
        user_settings.is_can_offer = community.main_settings.is_can_offer
        user_settings.is_minority_not_participate = (
            community.main_settings.is_minority_not_participate
        )
        user_settings.categories = list(filter(
            lambda it: it.status.code != Code.SYSTEM_CATEGORY,
            community.main_settings.categories))
        user_settings.sub_communities_settings = (
            community.main_settings.sub_communities_settings
        )
        user_settings.is_not_delegate = False
        user_settings.is_default_add_member = False
        try:
            self._session.add(user_settings)
            await self._session.flush([user_settings])
            await self._session.refresh(user_settings)
        except Exception as e:
            raise Exception(f'Не удалось создать '
                            f'пользовательские настройки: {e.__str__()}')

        return user_settings, True

    async def _update_parent_request_member(
            self, request_member: RequestMember
    ) -> None:
        request_member.status = (
            await self.get_status_by_code(Code.COMMUNITY_MEMBER)
        )
        request_member.updated = datetime.now()
        await self._session.flush([request_member])

    async def _create_child_request_members(
            self,
            parent_request_member: RequestMember,
    ) -> None:
        query = (
            select(RequestMember)
            .options(
                selectinload(RequestMember.member),
                selectinload(RequestMember.community),
                selectinload(RequestMember.status),
            )
            .where(
                RequestMember.community_id ==
                parent_request_member.community_id,
                RequestMember.parent_id.is_(None),
            )
        )
        request_members = await self._session.scalars(query)

        for request_member in list(request_members):
            child_request_member = self._create_copy_request_member(
                request_member
            )
            child_request_member.creator_id = parent_request_member.creator_id
            child_request_member.parent_id = request_member.id
            if request_member.id == parent_request_member.id:
                status = await self.get_status_by_code(Code.VOTED)
            else:
                status = await self.get_status_by_code(Code.VOTED_BY_DEFAULT)
            child_request_member.status = status
            try:
                self._session.add(child_request_member)
            except Exception as e:
                logger.error(f'Дочерний запрос на добавление члена сообщества '
                             f'(родителя с id {request_member.id}) не может '
                             f'быть создан: {e.__str__()}')
                continue

    async def _check_and_delete_user_settings(
            self, community_id: str,
            user_id: str
    ) -> None:
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
            except Exception as e:
                logger.error(
                f'Не удалось удались пользовательские настройки '
                f'сообщества с id: {user_settings.id}: {e.__str__()}'
                )

    async def _get_request_member(
            self,
            request_member_id: str,
            with_options: bool = True,
    ) -> Optional[RequestMember]:
        options = [
            selectinload(RequestMember.member),
            selectinload(RequestMember.community),
            selectinload(RequestMember.status),
        ] if with_options else []

        query = (
            select(RequestMember)
            .options(*options)
            .where(RequestMember.id == request_member_id)
        )
        return await self._session.scalar(query)

    async def _get_child_community_id(
            self, community_id: str
    ) -> Optional[str]:
        query = select(Community.parent_id).where(Community.id == community_id)
        result = await self._session.execute(query)
        row = result.fetchone()

        return row[0] if row else None

    async def _get_child_request_members(
            self,
            request_member_id: str,
    ) -> List[RequestMember]:
        query = select(RequestMember).where(
            RequestMember.parent_id == request_member_id
        )
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

    async def _create_child_request_members_after_main(
            self,
            request_member: RequestMember
    ) -> None:
        """Создание дочерних запросов на членство,
         после создания основного запроса.
        """
        user_cs_query = (
            select(
                UserCommunitySettings.id,
                UserCommunitySettings.is_default_add_member,
                UserCommunitySettings.user_id,
            ).where(
                UserCommunitySettings.community_id ==
                request_member.community_id
            )
        )
        user_cs_data = await self._session.execute(user_cs_query)
        user_cs_list = user_cs_data.all()

        for id_, is_default_add_member, user_id in user_cs_list:
            child_request_member = self._create_copy_request_member(
                request_member
            )
            child_request_member.parent_id = request_member.id
            child_request_member.creator_id = user_id
            if is_default_add_member or request_member.member.id == user_id:
                status_query = select(Status).where(Status.code == Code.VOTED)
                status = await self._session.scalar(status_query)
                child_request_member.vote = True
                child_request_member.status = status
            try:
                self._session.add(child_request_member)
            except Exception as e:
                logger.error(f'Дочерний запрос на добавление члена сообщества '
                             f'(родителя с id {request_member.id}) не может '
                             f'быть создан: {e.__str__()}')
                continue

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

    async def _create_new_voting_results(
            self, request_member: RequestMember
    ) -> None:
        """Создание пользовательских результатов голосований
        при вступлении нового участника в сообщество.
        """
        query = (
            select(
                UserVotingResult.voting_result_id,
                func.max(UserVotingResult.initiative_id)
                .label('initiative_id'),
                func.max(UserVotingResult.rule_id).label('rule_id'),
            )
            .where(
                UserVotingResult.community_id == request_member.community_id
            )
            .group_by(UserVotingResult.voting_result_id)
        )

        grouped_results = (await self._session.execute(query)).all()
        voting_result_ids = [row.voting_result_id for row in grouped_results]

        related_query = (
            select(VotingResult)
            .where(VotingResult.id.in_(voting_result_ids))
        )

        related_results = {
            row.id: row
            for row in (
                await self._session.execute(related_query)
            ).scalars().all()
        }

        for row in grouped_results:
            voting_result = related_results.get(row.voting_result_id)
            option_ids = list((voting_result.options or {}).keys())
            options = (
                await self._get_options_by_ids(option_ids)
                if option_ids else []
            )
            user_voting_result = UserVotingResult()
            user_voting_result.vote = voting_result.vote
            user_voting_result.extra_options = options
            user_voting_result.member_id = request_member.member_id
            user_voting_result.community_id = request_member.community_id
            user_voting_result.voting_result = voting_result
            user_voting_result.initiative_id = row.initiative_id
            user_voting_result.rule_id = row.rule_id
            user_voting_result.is_voted_by_default = True

            try:
                self._session.add(user_voting_result)
            except Exception as e:
                raise Exception(
                    f'Не удалось создать пользовательский '
                    f'результат голосования: {e.__str__()}'
                )

    async def _get_options_by_ids(self, ids: List[str]) -> List[VotingOption]:
        query = (
            select(VotingOption)
            .where(VotingOption.id.in_(ids))
        )
        result = await self._session.scalars(query)

        return list(result)
