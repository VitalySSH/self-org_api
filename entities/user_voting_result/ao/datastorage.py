from sqlalchemy import select, func
from typing import List, Optional, Union, Tuple

from core.dataclasses import BaseVotingParams
from datastorage.ao.base import AODataStorage
from datastorage.consts import Code
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.models import RelationUserVrVo
from datastorage.decorators import ds_async_with_new_session
from entities.initiative.model import Initiative
from entities.rule.model import Rule
from entities.user_voting_result.ao.interfaces import Resource, ResourceType
from entities.user_voting_result.model import UserVotingResult
from entities.voting_option.model import VotingOption
from entities.voting_result.model import VotingResult


class UserVotingResultDS(AODataStorage[UserVotingResult], CRUDDataStorage):

    _model = UserVotingResult

    @ds_async_with_new_session
    async def recount_vote(self, result_id: str) -> None:
        """Пересчитает результаты голосования."""
        user_voting_result: UserVotingResult = await self.get(
            instance_id=result_id, include=['extra_options'])
        voting_result: VotingResult = await self.get(
            instance_id=user_voting_result.voting_result_id,
            include=['selected_options'],
            model=VotingResult,
        )
        resource, resource_type = await self._get_resource(user_voting_result)
        last_vote = voting_result.vote
        last_status_code = resource.status.code
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
                    voting_result.selected_options = (
                        await self._get_new_selected_options(
                            user_voting_result=user_voting_result,
                            voting_params=community_voting_params
                        )
                    )
                    is_selected_options = (
                            len(voting_result.selected_options) > 0
                    )

            else:
                voting_result.vote = False
                if resource.is_extra_options:
                    voting_result.selected_options = []

        else:
            if last_vote:
                voting_result.vote = False
            if resource.is_extra_options:
                voting_result.selected_options = []

        await self._update_status_in_resource(
            resource=resource,
            resource_type=resource_type,
            last_status_code=last_status_code,
            is_selected_options=is_selected_options,
            is_quorum=is_quorum,
            is_decision=is_decision,
        )
        await self._session.commit()

    async def _update_status_in_resource(
            self, resource: Resource,
            resource_type: ResourceType,
            last_status_code: str,
            is_selected_options: bool,
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
                    status = await self.get_status_by_code(Code.RULE_APPROVED)
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
                    status = await self.get_status_by_code(
                        Code.INITIATIVE_APPROVED
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
            return await self.get(
                instance_id=rule_id,
                include=['status'],
                model=Rule,
            ), 'rule'
        elif initiative_id:
            return await self.get(
                instance_id=initiative_id,
                include=['status'],
                model=Initiative,
            ), 'initiative'

        else:
            raise Exception(
                f'Пользовательский результат голосования с id: '
                f'{user_voting_result.id} не имеет связи с источником'
            )

    async def _get_new_selected_options(
            self, user_voting_result: UserVotingResult,
            voting_params: BaseVotingParams,
    ) -> List[VotingOption]:
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
            return []

        min_count = (voting_params.vote / 100) * total_count

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
            func.count(RelationUserVrVo.to_id) >= min_count
        )

        option_counts_result = await self._session.execute(option_counts_query)
        options_data = option_counts_result.all()

        return [item[1] for item in options_data]
