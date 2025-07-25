import logging
from typing import Optional, Tuple, Dict, List, cast

from sqlalchemy import text, select, func, case, distinct
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dataclasses import (
    BaseVotingParams, SimpleVoteResult, BaseTimeParams
)
from datastorage.database.models import (
    Initiative, Rule, RequestMember, UserCommunitySettings, UserVotingResult,
    VotingOption, VotingResult, Status, RelationUserVrNoncompliance,
    Noncompliance
)
from datastorage.ao.interfaces import AO
from datastorage.base import DataStorage
from datastorage.consts import Code
from datastorage.database.models import RelationUserVrVo
from datastorage.interfaces import T
from entities.noncompliance.crud.dataclasses import NoncomplianceData
from entities.user_voting_result.ao.interfaces import Resource, ResourceType
from entities.voting_option.dataclasses import VotingOptionData

logger = logging.getLogger(__name__)


class AODataStorage(DataStorage[T], AO):
    """Дополнительная бизнес-логика для модели."""

    def __init__(
            self,
            session: Optional[AsyncSession] = None,
    ) -> None:
        super().__init__(model=self.__class__._model, session=session)

    async def calc_workgroup_size(self, community_id: str) -> int:
        """Вычислит размер рабочих групп для сообщества."""
        query = text("""
            WITH filtered_data AS (
                SELECT 
                    workgroup,
                    COUNT(*) OVER () AS total_count
                FROM public.user_community_settings
                WHERE community_id = :community_id 
                  AND is_blocked IS NOT TRUE AND is_workgroup IS TRUE
            ),
            ranked_data AS (
                SELECT 
                    workgroup,
                    ROW_NUMBER() OVER (ORDER BY workgroup) AS row_num_workgroup,
                    total_count
                FROM filtered_data
            ),
            median_values AS (
                SELECT 
                    AVG(CASE WHEN row_num_workgroup IN ((total_count + 1) / 2, (total_count + 2) / 2) 
                        THEN workgroup ELSE NULL END) AS workgroup_median
                FROM ranked_data
                WHERE 
                    row_num_workgroup IN ((total_count + 1) / 2, (total_count + 2) / 2)
            )
            SELECT 
                ROUND(COALESCE(workgroup_median, 0))
            FROM median_values;
        """)

        data = await self._session.execute(
            query, {'community_id': community_id}
        )
        row = data.fetchone()

        return int(row[0])

    async def calc_voting_params(
            self, community_id: str
    ) -> BaseVotingParams:
        """Вычислит основные параметры голосований
        для сообщества на текущий момент."""
        query = text("""
            WITH filtered_data AS (
                SELECT 
                    quorum,
                    vote,
                    significant_minority,
                    COUNT(*) OVER () AS total_count
                FROM public.user_community_settings
                WHERE community_id = :community_id 
                  AND is_blocked IS NOT TRUE
            ),
            ranked_data AS (
                SELECT 
                    quorum,
                    vote,
                    significant_minority,
                    ROW_NUMBER() OVER (ORDER BY quorum) AS row_num_quorum,
                    ROW_NUMBER() OVER (ORDER BY vote) AS row_num_vote,
                    ROW_NUMBER() OVER (ORDER BY significant_minority) AS row_num_minority,
                    total_count
                FROM filtered_data
            ),
            median_values AS (
                SELECT 
                    AVG(CASE WHEN row_num_quorum IN ((total_count + 1) / 2, (total_count + 2) / 2) 
                        THEN quorum ELSE NULL END) AS quorum_median,
                    AVG(CASE WHEN row_num_vote IN ((total_count + 1) / 2, (total_count + 2) / 2) 
                        THEN vote ELSE NULL END) AS vote_median,
                    AVG(CASE WHEN row_num_minority IN ((total_count + 1) / 2, (total_count + 2) / 2) 
                        THEN significant_minority ELSE NULL END) AS minority_median
                FROM ranked_data
                WHERE 
                    row_num_quorum IN ((total_count + 1) / 2, (total_count + 2) / 2) OR
                    row_num_vote IN ((total_count + 1) / 2, (total_count + 2) / 2) OR
                    row_num_minority IN ((total_count + 1) / 2, (total_count + 2) / 2)
            )
            SELECT 
                ROUND(COALESCE(quorum_median, 0)) AS quorum_median,
                ROUND(COALESCE(vote_median, 0)) AS vote_median,
                ROUND(COALESCE(minority_median, 0)) AS minority_median
            FROM median_values;
        """)

        data = await self._session.execute(
            query, {'community_id': community_id})
        quorum_median, vote_median, minority_median = data.fetchone()

        return BaseVotingParams(
            vote=int(vote_median),
            quorum=int(quorum_median),
            significant_minority=int(minority_median),
        )

    async def calc_time_params(self, community_id: str) -> BaseTimeParams:
        """Вычисляет медианные значения для сроков сообщества."""
        query = text("""
            WITH filtered_data AS (
                SELECT 
                    decision_delay,
                    dispute_time_limit,
                    COUNT(*) FILTER (WHERE decision_delay IS NOT NULL) OVER () AS delay_count,
                    COUNT(*) FILTER (WHERE dispute_time_limit IS NOT NULL) OVER () AS dispute_count
                FROM public.user_community_settings
                WHERE community_id = :community_id 
                  AND is_blocked IS NOT TRUE
            ),
            ranked_data AS (
                SELECT 
                    decision_delay,
                    dispute_time_limit,
                    ROW_NUMBER() OVER (ORDER BY decision_delay) AS delay_rank,
                    ROW_NUMBER() OVER (ORDER BY dispute_time_limit) AS dispute_rank
                FROM filtered_data
                WHERE decision_delay IS NOT NULL OR dispute_time_limit IS NOT NULL
            )
            SELECT 
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY decision_delay) AS median_delay,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dispute_time_limit) AS median_dispute
            FROM ranked_data;
        """)

        result = await self._session.execute(
            query, {'community_id': community_id})
        median_delay, median_dispute = result.fetchone()

        return BaseTimeParams(
            decision_delay=int(median_delay or 0),
            dispute_time_limit=int(median_dispute or 0),
        )

    async def recount_of_all_votes(
            self,
            community_id: str,
            voting_params: BaseVotingParams,
    ) -> None:
        """Пересчет всех голосов."""
        try:
            async with self._session.begin_nested():

                await self._recount_of_votes_by_requests_member(
                    community_id=community_id,
                    voting_params=voting_params
                )
                await self._recount_community_vote(
                    community_id=community_id,
                    voting_params=voting_params,
                )

        except SQLAlchemyError as e:
            logger.error(
                f'Ошибка при пересчете всех голосов:\n {e.__str__()}'
                f'Параметры: community_id={community_id}'
            )

    async def get_status_by_code(self, code: str) -> Optional[Status]:
        """Получить статус по коду."""
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def get_vote_in_percent(self, result_id: str) -> SimpleVoteResult:
        """Вернёт статистику по простому голосованию."""
        total_count_query = select(func.count()).where(
            UserVotingResult.voting_result_id == result_id,
            UserVotingResult.is_blocked.isnot(True),
        )
        total_count = await self._session.scalar(total_count_query)
        if total_count == 0:

            return SimpleVoteResult(yes=0, no=0, abstain=0)

        vote_counts_query = select(
            func.count(case((UserVotingResult.vote.is_(None), 1))),
            func.count(case((UserVotingResult.vote.is_(True), 1))),
            func.count(case((UserVotingResult.vote.is_(False), 1))),
        ).where(
            UserVotingResult.voting_result_id == result_id,
            UserVotingResult.is_blocked.isnot(True),
        )

        vote_counts_result = await self._session.execute(vote_counts_query)
        none_count, true_count, false_count = vote_counts_result.fetchone()

        abstain = (none_count / total_count) * 100
        yes = (true_count / total_count) * 100
        no = (false_count / total_count) * 100

        return SimpleVoteResult(yes=int(yes), no=int(no), abstain=int(abstain))

    async def update_vote_in_parent_requests_member(
            self,
            request_member: RequestMember,
            voting_params: Optional[BaseVotingParams] = None,
    ) -> None:
        """Обновление состояния основного запроса на членство
        через пересчёт голосов по дочерним запросам.
        """
        if voting_params is None:
            voting_params = await self.calc_voting_params(
            request_member.community_id
        )
        last_vote = request_member.vote
        last_status: Status = request_member.status
        vote_in_percent = await self.get_vote_stats_by_requests_member(
            request_member
        )
        is_quorum = (
                (vote_in_percent.yes + vote_in_percent.no) >=
                voting_params.quorum
        )
        is_decision = vote_in_percent.yes >= voting_params.vote
        new_vote = is_quorum and is_decision
        request_member.vote = new_vote

        if last_vote and not request_member.vote:
            if last_status.code == Code.COMMUNITY_MEMBER:
                request_member.status = await self.get_status_by_code(
                    Code.MEMBER_EXCLUDED
                )
                await self._block_user_settings(request_member)
            elif last_status.code == Code.REQUEST_SUCCESSFUL:
                request_member.status = await self.get_status_by_code(
                    Code.REQUEST_DENIED
                )
        elif not last_vote and request_member.vote:
            if last_status.code == Code.ON_CONSIDERATION:
                request_member.status = await self.get_status_by_code(
                    Code.REQUEST_SUCCESSFUL
                )
            elif last_status.code == Code.MEMBER_EXCLUDED:
                request_member.status = await self.get_status_by_code(
                    Code.COMMUNITY_MEMBER
                )
                await self._unblock_user_settings(request_member)
            elif last_status.code == Code.REQUEST_DENIED:
                request_member.status = await self.get_status_by_code(
                    Code.REQUEST_SUCCESSFUL
                )

    async def user_vote_count(
            self, voting_result: VotingResult,
            resource: Resource,
            resource_type: ResourceType,
            voting_params: Optional[BaseVotingParams] = None,
    ) -> None:
        """Подсчет голосов."""
        if voting_params is None:
            voting_params = await self.calc_voting_params(
                cast(str, resource.community_id)
            )

        last_vote = voting_result.vote
        last_status = resource.status
        is_significant_minority = voting_result.is_significant_minority
        is_noncompliance_minority = voting_result.is_noncompliance_minority
        vote_in_percent = await self.get_vote_in_percent(voting_result.id)
        is_selected_options = False
        is_selected_noncompliance = False
        is_quorum = (
                (vote_in_percent.yes + vote_in_percent.no) >=
                voting_params.quorum
        )
        is_decision = vote_in_percent.yes >= voting_params.vote
        if is_quorum:

            if is_decision:
                voting_result.vote = True

                if resource.is_extra_options:
                    options, minority_options = (
                        await self._get_new_selected_options(
                            resource=resource,
                            resource_type=resource_type,
                            voting_params=voting_params
                        )
                    )
                    is_significant_minority = bool(minority_options)
                    is_selected_options = bool(options)
                    voting_result.options = options
                    voting_result.is_significant_minority = (
                        is_significant_minority
                    )
                    voting_result.minority_options = minority_options

                selected_noncompliance, minority_noncompliance = (
                    await self._get_new_noncompliance(
                        resource=resource,
                        resource_type=resource_type,
                        voting_params=voting_params
                    )
                )
                is_noncompliance_minority = bool(minority_noncompliance)
                is_selected_noncompliance = bool(selected_noncompliance)
                voting_result.noncompliance = selected_noncompliance
                voting_result.is_noncompliance_minority = (
                    is_noncompliance_minority
                )
                voting_result.minority_noncompliance = minority_noncompliance

            else:
                voting_result.vote = False
                voting_result.is_significant_minority = False
                voting_result.is_noncompliance_minority = False
                if resource.is_extra_options:
                    voting_result.options = {}
                    voting_result.minority_options = {}
                if resource_type == 'rule':
                    voting_result.noncompliance = {}
                    voting_result.minority_noncompliance = {}


        else:
            if last_vote:
                voting_result.vote = False
            if is_significant_minority:
                voting_result.is_significant_minority = False
            if is_noncompliance_minority:
                voting_result.is_noncompliance_minority = False
            if resource.is_extra_options:
                voting_result.options = {}
                voting_result.minority_options = {}
            if resource_type == 'rule':
                voting_result.noncompliance = {}
                voting_result.minority_noncompliance = {}

        await self._update_status_in_resource(
            resource=resource,
            resource_type=resource_type,
            last_status=cast(Status, last_status),
            is_selected_options=is_selected_options,
            is_significant_minority=is_significant_minority,
            is_selected_noncompliance=is_selected_noncompliance,
            is_noncompliance_minority=is_noncompliance_minority,
            is_quorum=is_quorum,
            is_decision=is_decision,
        )

    async def _update_status_in_resource(
            self, resource: Resource,
            resource_type: ResourceType,
            last_status: Status,
            is_selected_options: bool,
            is_significant_minority: bool,
            is_selected_noncompliance: bool,
            is_noncompliance_minority: bool,
            is_quorum: bool,
            is_decision: bool,
    ) -> None:
        status = resource.status
        match resource_type:
            case 'rule':
                if (last_status.code == Code.RULE_APPROVED and
                        (not is_quorum or not is_decision or
                         (resource.is_extra_options and
                          not is_selected_options) or
                         not is_selected_noncompliance)):
                    status = await self.get_status_by_code(Code.RULE_REVOKED)
                elif (is_quorum and is_decision and (
                        (resource.is_extra_options and is_selected_options) or
                        not resource.is_extra_options) and
                      is_selected_noncompliance):
                    if is_significant_minority or is_noncompliance_minority:
                        status = await self.get_status_by_code(
                            Code.COMPROMISE
                        )
                    else:
                        status = await self.get_status_by_code(
                            Code.RULE_APPROVED
                        )
                elif (is_quorum and is_decision and
                      ((resource.is_extra_options and not is_selected_options)
                       or not is_selected_noncompliance)
                      and last_status.code != Code.RULE_REVOKED):
                    status = await self.get_status_by_code(
                        Code.PRINCIPAL_AGREEMENT
                    )
                else:
                    if last_status.code == Code.RULE_REVOKED:
                        status = last_status
                    else:
                        status = await self.get_status_by_code(
                            Code.ON_CONSIDERATION
                        )
            case 'initiative':
                if (last_status.code == Code.INITIATIVE_APPROVED and
                        (not is_quorum or not is_decision or
                         (resource.is_extra_options and
                          not is_selected_options))):
                    status = await self.get_status_by_code(
                        Code.INITIATIVE_REVOKED
                    )
                elif (is_quorum and is_decision and (
                        (resource.is_extra_options and is_selected_options)
                        or not resource.is_extra_options)):
                    if is_significant_minority:
                        status = await self.get_status_by_code(
                            Code.COMPROMISE
                        )
                    else:
                        status = await self.get_status_by_code(
                            Code.INITIATIVE_APPROVED
                        )
                elif (is_quorum and is_decision and
                      (resource.is_extra_options and
                       not is_selected_options) and
                      last_status.code != Code.INITIATIVE_REVOKED):
                    status = await self.get_status_by_code(
                        Code.PRINCIPAL_AGREEMENT
                    )
                else:
                    if last_status.code == Code.INITIATIVE_REVOKED:
                        status = last_status
                    else:
                        status = await self.get_status_by_code(
                            Code.ON_CONSIDERATION
                        )

        resource.status = status

    async def _get_new_selected_options(
            self,
            resource: Resource,
            resource_type: ResourceType,
            voting_params: BaseVotingParams,
    ) -> Tuple[Dict[str, VotingOptionData], Dict[str, VotingOptionData]]:
        filters = [UserVotingResult.is_blocked.isnot(True)]
        match resource_type:
            case 'rule':
                filters.append(UserVotingResult.rule_id == resource.id)
            case 'initiative':
                filters.append(UserVotingResult.initiative_id == resource.id)

        total_users_query = select(
            func.count(distinct(UserVotingResult.member_id))
        ).where(*filters)
        total_users = await self._session.scalar(total_users_query)

        if total_users == 0:
            return {}, {}

        min_count = (voting_params.vote / 100) * total_users
        min_count_minority = (
                (voting_params.significant_minority / 100) * total_users
        )

        # Шаг 1: Получаем веса всех вариантов
        weight_subquery = (
            select(
                RelationUserVrVo.to_id.label('option_id'),
                UserVotingResult.id.label('user_result_id'),
                (1.0 / func.count(RelationUserVrVo.to_id).over(
                    partition_by=UserVotingResult.id
                )).label('weight')
            )
            .join(UserVotingResult,
                  UserVotingResult.id == RelationUserVrVo.from_id)
            .where(*filters)
        ).subquery()

        # Шаг 2: Агрегируем веса по вариантам
        all_options_query = (
            select(
                weight_subquery.c.option_id,
                func.sum(weight_subquery.c.weight).label('total_weight'),
                VotingOption
            )
            .join(VotingOption,
                  VotingOption.id == weight_subquery.c.option_id)
            .group_by(weight_subquery.c.option_id, VotingOption.id)
        )

        all_options_result = await self._session.execute(all_options_query)
        all_options_data = all_options_result.all()

        if not all_options_data:
            return {}, {}

        # Шаг 3: Определяем победителей в зависимости от is_multi_select
        winners = {}
        winner_ids = set()

        sorted_all_options = sorted(all_options_data,
                                    key=lambda x: x.total_weight, reverse=True)

        if resource.is_multi_select:
            # Множественный результат: все варианты, преодолевшие порог
            for idx, (option_id, weight, voting_option) in enumerate(
                    sorted_all_options, 1):
                if weight >= min_count:
                    percent = int((weight / total_users) * 100)
                    winners[option_id] = VotingOptionData(
                        number=idx,
                        value=voting_option.content,
                        percent=percent,
                    )
                    winner_ids.add(option_id)
        else:
            # Единственный результат: только лидер, если он преодолел порог
            if sorted_all_options:
                option_id, weight, voting_option = sorted_all_options[0]
                if weight >= min_count:
                    percent = int((weight / total_users) * 100)
                    winners[option_id] = VotingOptionData(
                        number=1,
                        value=voting_option.content,
                        percent=percent,
                    )
                    winner_ids.add(option_id)

        # Шаг 4: Находим голосующих, которые НЕ поддержали ни одного победителя
        minority = {}

        if winner_ids:
            # Подзапрос: пользователи, которые голосовали за победителей
            users_voted_for_winners = (
                select(distinct(UserVotingResult.id))
                .join(RelationUserVrVo,
                      UserVotingResult.id == RelationUserVrVo.from_id)
                .where(
                    *filters,
                    RelationUserVrVo.to_id.in_(winner_ids)
                )
            ).scalar_subquery()

            # Фильтр для голосующих, которые НЕ поддержали победителей
            minority_filters = filters + [
                UserVotingResult.id.notin_(users_voted_for_winners)
            ]

            # Шаг 5: Пересчитываем веса для меньшинства
            minority_weight_subquery = (
                select(
                    RelationUserVrVo.to_id.label('option_id'),
                    (1.0 / func.count(RelationUserVrVo.to_id).over(
                        partition_by=UserVotingResult.id
                    )).label('weight')
                )
                .join(UserVotingResult,
                      UserVotingResult.id == RelationUserVrVo.from_id)
                .where(*minority_filters)
            ).subquery()

            # Шаг 6: Агрегируем веса меньшинства (исключая победителей)
            minority_options_query = (
                select(
                    minority_weight_subquery.c.option_id,
                    func.sum(minority_weight_subquery.c.weight).label(
                        'total_weight'),
                    VotingOption
                )
                .join(VotingOption,
                      VotingOption.id == minority_weight_subquery.c.option_id)
                .where(minority_weight_subquery.c.option_id.notin_(winner_ids))
                .group_by(minority_weight_subquery.c.option_id,
                          VotingOption.id)
                .having(
                    func.sum(
                        minority_weight_subquery.c.weight) >= min_count_minority
                )
            )

            minority_result = await self._session.execute(
                minority_options_query)
            minority_data = minority_result.all()

            # Шаг 7: Формируем результат меньшинства
            for idx, (option_id, weight, voting_option) in enumerate(
                    sorted(minority_data, key=lambda x: x.total_weight,
                           reverse=True), 1
            ):
                # Процент рассчитываем от общего числа пользователей
                percent = int((weight / total_users) * 100)
                minority[option_id] = VotingOptionData(
                    number=idx,
                    value=voting_option.content,
                    percent=percent,
                )
        else:
            # Если нет победителей, все варианты,
            # преодолевшие порог меньшинства, попадают в minority
            for idx, (option_id, weight, voting_option) in enumerate(
                    sorted_all_options, 1):
                if weight >= min_count_minority:
                    percent = int((weight / total_users) * 100)
                    minority[option_id] = VotingOptionData(
                        number=idx,
                        value=voting_option.content,
                        percent=percent,
                    )

        return winners, minority

    async def _get_new_noncompliance(
            self,
            resource: Resource,
            resource_type: ResourceType,
            voting_params: BaseVotingParams,
    ) -> Tuple[Dict[str, NoncomplianceData], Dict[str, NoncomplianceData]]:
        if resource_type == 'initiative':
            return {}, {}

        filters = [
            UserVotingResult.is_blocked.isnot(True),
            UserVotingResult.rule_id == resource.id,
        ]

        # Шаг 1: Получаем все веса для noncompliance
        all_weight_subquery = (
            select(
                RelationUserVrNoncompliance.to_id.label('nc_id'),
                UserVotingResult.id.label('user_result_id'),
                (1.0 / func.count(RelationUserVrNoncompliance.to_id).over(
                    partition_by=UserVotingResult.id
                )).label('weight')
            )
            .join(UserVotingResult,
                  UserVotingResult.id == RelationUserVrNoncompliance.from_id)
            .where(*filters)
        ).subquery()

        # Шаг 2: Агрегируем все веса
        all_nc_query = (
            select(
                all_weight_subquery.c.nc_id,
                func.sum(all_weight_subquery.c.weight).label('total_weight'),
                Noncompliance
            )
            .join(Noncompliance,
                  Noncompliance.id == all_weight_subquery.c.nc_id)
            .group_by(all_weight_subquery.c.nc_id, Noncompliance.id)
        )

        all_nc_result = await self._session.execute(all_nc_query)
        all_nc_data = all_nc_result.all()

        if not all_nc_data:
            return {}, {}

        total_weight = sum(row.total_weight for row in all_nc_data)
        if total_weight <= 0:
            return {}, {}

        min_weight = (voting_params.vote / 100) * total_weight
        min_minority = (
                                   voting_params.significant_minority / 100) * total_weight

        # Шаг 3: Определяем победителей среди noncompliance
        winners = {}
        winner_ids = set()
        leader_weight = None

        sorted_all_nc = sorted(all_nc_data, key=lambda x: x.total_weight,
                               reverse=True)

        for idx, (nc_id, weight, noncompliance) in enumerate(sorted_all_nc, 1):
            if weight >= min_weight:
                if not winners:
                    winners[nc_id] = NoncomplianceData(
                        number=idx,
                        value=noncompliance.name,
                        percent=int((weight / total_weight) * 100),
                    )
                    winner_ids.add(nc_id)
                    leader_weight = weight
                elif weight == leader_weight:
                    # Если есть равные лидеры, очищаем победителей (нет единого лидера)
                    winners.clear()
                    winner_ids.clear()
                    break
                else:
                    break

        # Шаг 4: Если есть победители, вычисляем меньшинство по новой логике
        minority_nc = {}

        if winner_ids:
            # Находим пользователей, которые НЕ голосовали за победителей
            users_voted_for_winners = (
                select(distinct(UserVotingResult.id))
                .join(RelationUserVrNoncompliance,
                      UserVotingResult.id == RelationUserVrNoncompliance.from_id)
                .where(
                    *filters,
                    RelationUserVrNoncompliance.to_id.in_(winner_ids)
                )
            ).scalar_subquery()

            minority_filters = filters + [
                UserVotingResult.id.notin_(users_voted_for_winners)
            ]

            # Пересчитываем веса для меньшинства
            minority_weight_subquery = (
                select(
                    RelationUserVrNoncompliance.to_id.label('nc_id'),
                    (1.0 / func.count(RelationUserVrNoncompliance.to_id).over(
                        partition_by=UserVotingResult.id
                    )).label('weight')
                )
                .join(UserVotingResult,
                      UserVotingResult.id == RelationUserVrNoncompliance.from_id)
                .where(*minority_filters)
            ).subquery()

            minority_nc_query = (
                select(
                    minority_weight_subquery.c.nc_id,
                    func.sum(minority_weight_subquery.c.weight).label(
                        'total_weight'),
                    Noncompliance
                )
                .join(Noncompliance,
                      Noncompliance.id == minority_weight_subquery.c.nc_id)
                .where(minority_weight_subquery.c.nc_id.notin_(winner_ids))
                .group_by(minority_weight_subquery.c.nc_id, Noncompliance.id)
            )

            minority_nc_result = await self._session.execute(minority_nc_query)
            minority_nc_data = minority_nc_result.all()

            if minority_nc_data:
                minority_min_weight = (
                    (voting_params.significant_minority / 100) * total_weight
                )  # От общего веса

                for idx, (nc_id, weight, noncompliance) in enumerate(
                        sorted(minority_nc_data, key=lambda x: x.total_weight,
                               reverse=True), 1
                ):
                    if weight >= minority_min_weight:
                        percent = int(
                            (weight / total_weight) * 100)  # От общего веса
                        minority_nc[nc_id] = NoncomplianceData(
                            number=idx,
                            value=noncompliance.name,
                            percent=percent,
                        )
        else:
            # Если нет победителей, применяем старую логику для меньшинства
            for idx, (nc_id, weight, noncompliance) in enumerate(sorted_all_nc, 1):
                if weight >= min_minority:
                    percent = int((weight / total_weight) * 100)
                    minority_nc[nc_id] = NoncomplianceData(
                        number=idx,
                        value=noncompliance.name,
                        percent=percent,
                    )

        return winners, minority_nc

    async def _block_user_settings(
            self, request_member: RequestMember
    ) -> None:
        query = (
            select(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id ==
                request_member.community_id,
                UserCommunitySettings.user_id == request_member.member_id,
                UserCommunitySettings.is_blocked.is_not(True),
            )
        )
        user_settings = await self._session.scalar(query)
        if user_settings:
            user_settings.is_blocked = True
        #  Блокируем голосования пользователя.
        await self._update_user_voting_results(
            member_id=request_member.member_id,
            value=True
        )
        #  Пересчитываем голоса в голосованиях.
        await self._recount_community_vote(request_member.community_id)

    async def _unblock_user_settings(
            self, request_member: RequestMember
    ) -> None:
        query = (
            select(UserCommunitySettings)
            .where(
                UserCommunitySettings.community_id ==
                request_member.community_id,
                UserCommunitySettings.user_id == request_member.member_id,
                UserCommunitySettings.is_blocked.is_(True),
            )
        )
        user_settings = await self._session.scalar(query)
        if user_settings:
            user_settings.is_blocked = False
        #  Разблокируем голосования пользователя.
        await self._update_user_voting_results(
            member_id=request_member.member_id,
            value=False
        )
        #  Пересчитываем голоса в голосованиях.
        await self._recount_community_vote(request_member.community_id)

    async def get_vote_stats_by_requests_member(
            self,
            request_member: RequestMember
    ) -> SimpleVoteResult:
        vote_true = func.sum(case(
            (RequestMember.vote.is_(True), 1), else_=0)
        )
        vote_false = func.sum(case(
            (RequestMember.vote.is_(False), 1), else_=0)
        )
        vote_null = func.sum(case(
            (RequestMember.vote.is_(None), 1), else_=0)
        )
        total_count = func.count(RequestMember.id)

        query = (
            select(
                vote_true.label('yes_count'),
                vote_false.label('no_count'),
                vote_null.label('abstain_count'),
                total_count.label('total')
            )
            .where(
                RequestMember.parent_id == request_member.id,
            )
        )

        result = await self._session.execute(query)
        row = result.first()

        if not row or row.total == 0:
            return SimpleVoteResult(yes=0, no=0, abstain=0)

        yes = int((row.yes_count / row.total) * 100)
        no = int((row.no_count / row.total) * 100)
        abstain = int((row.abstain_count / row.total) * 100)

        return SimpleVoteResult(yes=yes, no=no, abstain=abstain)

    async def _update_user_voting_results(
            self, member_id: str,
            value: bool
    ) -> None:
        query = text("""
            UPDATE public.user_voting_result
            SET is_blocked = :is_blocked
            WHERE member_id = :member_id
        """)
        try:
            async with self._session.begin_nested():

                await self._session.execute(
                    query,
                    {'member_id': member_id, 'is_blocked': value}
                )

        except SQLAlchemyError as e:
            logger.error(
                f'Ошибка при обновлении пользовательских '
                f'результатов голосований: {e.__str__()}.\n'
                f'Параметры: member_id={member_id}, value={str(value)}'
            )

    async def _delete_user_voting_results(self, member_id: str) -> None:
        query = text("""
            DELETE FROM public.user_voting_result
            WHERE member_id = :member_id
        """)
        try:
            async with self._session.begin_nested():

                await self._session.execute(
                    query, {'member_id': member_id}
                )

        except SQLAlchemyError as e:
            logger.error(
                f'Ошибка при удалении пользовательских '
                f'результатов голосований: {e.__str__()}.\n'
                f'Параметры: member_id={member_id}'
            )

    async def _recount_community_vote(
            self,
            community_id: str,
            voting_params: Optional[BaseVotingParams] = None,
    ) -> None:
        """Пересчёт голосов по всем голосованиям сообщества."""
        if voting_params is None:
            voting_params = await self.calc_voting_params(community_id)

        rules: List[Rule] = await self._get_community_rules(community_id)
        for rule in rules:
            await self.user_vote_count(
                voting_result=rule.voting_result,
                resource=rule,
                resource_type='rule',
                voting_params=voting_params,
            )

        initiatives: List[Initiative] = (
            await self._get_community_initiatives(community_id)
        )
        for initiative in initiatives:
            await self.user_vote_count(
                voting_result=initiative.voting_result,
                resource=initiative,
                resource_type='initiative',
                voting_params=voting_params,
            )

    async def _get_community_rules(self, community_id: str) -> List[Rule]:
        query = (
            select(Rule)
            .options(
                selectinload(Rule.status),
                selectinload(Rule.voting_result),
            )
            .where(Rule.community_id == community_id)
        )
        rows = await self._session.scalars(query)

        return list(rows)

    async def _get_community_initiatives(
            self,
            community_id: str
    ) -> List[Initiative]:
        query = (
            select(Initiative)
            .options(
                selectinload(Initiative.status),
                selectinload(Initiative.voting_result),
            )
            .where(Initiative.community_id == community_id)
        )
        rows = await self._session.scalars(query)

        return list(rows)

    async def _get_community_requests_member(
            self,
            community_id: str,
    ) -> List[RequestMember]:
        query = (
            select(RequestMember)
            .options(
                selectinload(RequestMember.member),
                selectinload(RequestMember.community),
                selectinload(RequestMember.status),
            )
            .where(
                RequestMember.community_id == community_id,
                RequestMember.parent_id.is_(None),
            )
        )
        rows = await self._session.scalars(query)

        return list(rows)

    async def _recount_of_votes_by_requests_member(
            self,
            community_id: str,
            voting_params: BaseVotingParams
    ) -> None:
        requests: List[RequestMember] = (
            await self._get_community_requests_member(community_id)
        )
        for _request in requests:
            await self.update_vote_in_parent_requests_member(
                request_member=_request,
                voting_params=voting_params,
            )
