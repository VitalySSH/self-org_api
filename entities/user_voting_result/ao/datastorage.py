from typing import Optional, Union, Tuple

from datastorage.ao.datastorage import AODataStorage
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.decorators import ds_async_with_new_session
from entities.initiative.model import Initiative
from entities.rule.model import Rule
from entities.user_voting_result.ao.interfaces import Resource, ResourceType
from entities.user_voting_result.model import UserVotingResult
from entities.voting_result.model import VotingResult


class UserVotingResultDS(
    AODataStorage[UserVotingResult],
    CRUDDataStorage[UserVotingResult]
):

    _model = UserVotingResult

    @ds_async_with_new_session
    async def recount_vote(self, result_id: str) -> None:
        """Пересчитает результаты голосования."""
        user_voting_result: UserVotingResult = await self.get(
            instance_id=result_id, include=['extra_options']
        )
        voting_result: Optional[VotingResult] = await self.get(
            instance_id=user_voting_result.voting_result_id,
            include=['selected_options'],
            model=VotingResult,
        )
        resource, resource_type = await self._get_resource(user_voting_result)
        await self.user_vote_count(
            voting_result=voting_result,
            resource=resource,
            resource_type=resource_type,
        )

    async def _get_resource(
            self, user_voting_result: UserVotingResult
    ) -> Union[Tuple[Optional[Resource], ResourceType], Exception]:
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
