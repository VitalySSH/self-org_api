from typing import Optional, Union, Tuple, List

from sqlalchemy import text, select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from core.dataclasses import BaseVotingParams, SimpleVoteResult
from datastorage.ao.interfaces import AO
from datastorage.base import DataStorage
from datastorage.consts import Code
from datastorage.database.models import RelationUserVrVo
from datastorage.interfaces import T
from entities.initiative.model import Initiative
from entities.rule.model import Rule
from entities.status.model import Status
from entities.user_voting_result.ao.interfaces import Resource, ResourceType
from entities.user_voting_result.model import UserVotingResult
from entities.voting_option.model import VotingOption
from entities.voting_result.model import VotingResult


class AODataStorage(DataStorage[T], AO):
    """Дополнительная бизнес-логика для модели."""

    def __init__(self, session: Optional[AsyncSession] = None):
        super().__init__(model=self.__class__._model, session=session)

    async def calculate_voting_params(
            self, community_id: str
    ) -> BaseVotingParams:
        """Вычислит основные параметры голосований
        для сообщества на текущий момент."""
        query = text("""
            WITH sorted_data AS (
                SELECT 
                    quorum,
                    vote,
                    significant_minority,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY quorum) AS row_num_quorum,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY vote) AS row_num_vote,
                    ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY significant_minority) AS row_num_minority,
                    COUNT(*) OVER (PARTITION BY community_id) AS total_count
                FROM public.user_community_settings
                WHERE community_id = :community_id AND is_blocked IS NOT TRUE
            )
            SELECT 
                ROUND(AVG(quorum)) AS quorum_median,
                ROUND(AVG(vote)) AS vote_median,
                ROUND(AVG(significant_minority)) AS minority_median
            FROM sorted_data
            WHERE 
                row_num_quorum IN ((total_count + 1) / 2, (total_count + 2) / 2)
                OR
                row_num_vote IN ((total_count + 1) / 2, (total_count + 2) / 2)
                OR
                row_num_minority IN ((total_count + 1) / 2, (total_count + 2) / 2);
        """)

        data = await self._session.execute(
            query, {'community_id': community_id})
        quorum_median, vote_median, minority_median = data.fetchone()

        return BaseVotingParams(
            vote=int(vote_median),
            quorum=int(quorum_median),
            significant_minority=int(minority_median),
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

    async def vote_count(self, result_id: str) -> None:
        """Подсчет голосов."""
        user_voting_result = await self._get_user_voting_result(result_id)
        voting_result = await self._get_voting_result(
            user_voting_result.voting_result_id
        )
        resource, resource_type = await self._get_resource(user_voting_result)
        last_vote = voting_result.vote
        last_status_code = resource.status.code
        is_significant_minority = voting_result.is_significant_minority
        community_voting_params = await self.calculate_voting_params(
            user_voting_result.community_id)
        vote_in_percent = await self.get_vote_in_percent(voting_result.id)
        is_selected_options = False
        is_quorum = (
                (vote_in_percent.yes + vote_in_percent.no) >=
                community_voting_params.quorum
        )
        is_decision = vote_in_percent.yes >= community_voting_params.vote
        if is_quorum:

            if is_decision:
                voting_result.vote = True

                if resource.is_extra_options:
                    selected_options, is_significant_minority = (
                        await self._get_new_selected_options(
                            user_voting_result=user_voting_result,
                            voting_params=community_voting_params
                        )
                    )
                    is_selected_options = len(selected_options) > 0
                    voting_result.selected_options = (
                        selected_options if resource.is_multi_select
                        else [selected_options[0]]
                        if selected_options else []
                    )
                    voting_result.is_significant_minority = (
                        is_significant_minority
                    )

            else:
                voting_result.vote = False
                voting_result.is_significant_minority = False
                if resource.is_extra_options:
                    voting_result.selected_options = []

        else:
            if last_vote:
                voting_result.vote = False
            if is_significant_minority:
                voting_result.is_significant_minority = False
            if resource.is_extra_options:
                voting_result.selected_options = []

        await self._update_status_in_resource(
            resource=resource,
            resource_type=resource_type,
            last_status_code=last_status_code,
            is_selected_options=is_selected_options,
            is_significant_minority=is_significant_minority,
            is_quorum=is_quorum,
            is_decision=is_decision,
        )
        await self._session.commit()

    async def _update_status_in_resource(
            self, resource: Resource,
            resource_type: ResourceType,
            last_status_code: str,
            is_selected_options: bool,
            is_significant_minority: bool,
            is_quorum: bool,
            is_decision: bool,
    ) -> None:
        status = resource.status
        match resource_type:
            case 'rule':
                if (last_status_code == Code.RULE_APPROVED and
                        (not is_quorum or not is_decision or
                         (resource.is_extra_options and
                          not is_selected_options))):
                    status = await self.get_status_by_code(Code.RULE_REVOKED)
                elif (is_quorum and is_decision and (
                        (resource.is_extra_options and is_selected_options)
                        or not resource.is_extra_options)):
                    if is_significant_minority:
                        status = await self.get_status_by_code(
                            Code.COMPROMISE
                        )
                    else:
                        status = await self.get_status_by_code(
                            Code.RULE_APPROVED
                        )
                elif (is_quorum and is_decision and
                      (resource.is_extra_options and not is_selected_options)):
                    status = await self.get_status_by_code(
                        Code.PRINCIPAL_AGREEMENT
                    )
                else:
                    status = await self.get_status_by_code(
                        Code.ON_CONSIDERATION
                    )
            case 'initiative':
                if (last_status_code == Code.INITIATIVE_APPROVED and
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
                            Code.RULE_APPROVED
                        )
                elif (is_quorum and is_decision and
                      (resource.is_extra_options and not is_selected_options)):
                    status = await self.get_status_by_code(
                        Code.PRINCIPAL_AGREEMENT
                    )
                else:
                    status = await self.get_status_by_code(
                        Code.ON_CONSIDERATION
                    )

        resource.status = status

    async def _get_resource(
            self, user_voting_result: UserVotingResult
    ) -> Union[Tuple[Resource, ResourceType], Exception]:
        rule_id: Optional[str] = user_voting_result.rule_id
        initiative_id: Optional[str] = user_voting_result.initiative_id
        if rule_id:
            return await self._get_rule(rule_id), 'rule'
        elif initiative_id:
            return await self._get_initiative(initiative_id), 'initiative'

        else:
            raise Exception(
                f'Пользовательский результат голосования с id: '
                f'{user_voting_result.id} не имеет связи с источником'
            )

    async def _get_new_selected_options(
            self, user_voting_result: UserVotingResult,
            voting_params: BaseVotingParams,
    ) -> Tuple[List[VotingOption], bool]:
        is_significant_minority = False
        filters = [UserVotingResult.is_blocked.isnot(True)]
        if user_voting_result.rule_id:
            filters.append(
                UserVotingResult.rule_id == user_voting_result.rule_id
            )
        elif user_voting_result.initiative_id:
            filters.append(
                UserVotingResult.initiative_id ==
                user_voting_result.initiative_id
            )
        else:
            raise Exception(
                f'Пользовательский результат голосования с id: '
                f'{user_voting_result.id} не имеет связи с источником'
            )
        total_count_query = (
            select(func.count(UserVotingResult.id)).where(*filters)
        )
        total_count_result = await self._session.execute(total_count_query)
        total_count = total_count_result.scalar_one()

        if total_count == 0:
            return [], is_significant_minority

        min_count = (voting_params.vote / 100) * total_count
        min_count_minority = (
                (voting_params.significant_minority / 100) * total_count
        )

        option_counts_query = select(
            VotingOption.id,
            VotingOption,
            func.count(RelationUserVrVo.to_id)
        ).join(
            RelationUserVrVo,
            RelationUserVrVo.to_id == VotingOption.id
        ).join(
            UserVotingResult,
            UserVotingResult.id == RelationUserVrVo.from_id
        ).where(
            *filters
        ).group_by(
            VotingOption.id
        ).having(
            func.count(RelationUserVrVo.to_id) >= min_count_minority
        )

        option_counts_result = await self._session.execute(option_counts_query)
        options_data = sorted(option_counts_result.all(),
                              key=lambda it: it[2], reverse=True)

        options: List[VotingOption] = []
        for item in options_data:
            count = item[2]
            if count >= min_count:
                options.append(item[1])
            else:
                if not is_significant_minority:
                    is_significant_minority = True

        return options, is_significant_minority

    async def _get_user_voting_result(
            self, result_id: str
    ) -> Optional[UserVotingResult]:
        query = (
            select(UserVotingResult)
            .where(UserVotingResult.id == result_id)
            .selectinload(UserVotingResult.extra_options)
        )
        return await self._session.scalar(query)

    async def _get_voting_result(
            self, result_id: str
    ) -> Optional[VotingResult]:
        query = (
            select(VotingResult)
            .where(VotingResult.id == result_id)
            .selectinload(VotingResult.selected_options)
        )
        return await self._session.scalar(query)

    async def _get_rule(self, rule_id: str) -> Optional[Rule]:
        query = (
            select(Rule)
            .where(Rule.id == rule_id)
            .selectinload(Rule.status)
        )
        return await self._session.scalar(query)

    async def _get_initiative(
            self, initiative_id: str
    ) -> Optional[Initiative]:
        query = (
            select(Initiative)
            .where(Initiative.id == initiative_id)
            .selectinload(Initiative.status)
        )
        return await self._session.scalar(query)
