from typing import Optional, Union, Tuple, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from datastorage.ao.datastorage import AODataStorage
from datastorage.crud.datastorage import CRUDDataStorage
from entities.user_voting_result.ao.interfaces import Resource, ResourceType
from datastorage.database.models import (
    VotingResult, VotingOption, UserVotingResult, Rule, Initiative,
    Noncompliance, DelegateSettings
)


class UserVotingResultDS(
    AODataStorage[UserVotingResult],
    CRUDDataStorage[UserVotingResult]
):

    _model = UserVotingResult

    async def recount_vote(self, result_id: str) -> None:
        """Пересчитает результаты голосования."""
        async with self.session_scope():
            user_voting_result: UserVotingResult = await self.get(
                instance_id=result_id,
                include=['extra_options', 'noncompliance']
            )
            voting_result: Optional[VotingResult] = await self.get(
                instance_id=user_voting_result.voting_result_id,
                model=VotingResult,
            )
            resource, resource_type = await self._get_resource(
                user_voting_result
            )
            await self._propagate_vote(
                user_id=user_voting_result.member_id,
                community_id=user_voting_result.community_id,
                category_id=resource.category_id,
                resource=resource,
                resource_type=resource_type,
                vote=user_voting_result.vote,
                extra_options=user_voting_result.extra_options,
                noncompliance=user_voting_result.noncompliance,
            )

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

    async def _propagate_vote(
            self, user_id: str,
            community_id: str,
            category_id: str,
            resource: Resource,
            resource_type: ResourceType,
            vote: bool,
            extra_options: List[VotingOption],
            noncompliance: List[Noncompliance],
    ) -> None:
        """Размножить голос от делегата к доверителям."""
        delegate_settings = await self._get_delegate_settings(
            user_id=user_id,
            community_id=community_id,
            category_id=category_id,
        )
        for delegate_setting in delegate_settings:
            target_user_id = delegate_setting.user_id
            filters = [
                UserVotingResult.member_id == target_user_id,
                UserVotingResult.community_id == community_id,
            ]
            match resource_type:
                case 'rule':
                    filters.append(UserVotingResult.rule_id == resource.id)
                case 'initiative':
                    filters.append(
                        UserVotingResult.initiative_id == resource.id
                    )

            user_voting_result: Optional[UserVotingResult] = (
                await self._session.scalar(
                    select(UserVotingResult)
                    .where(*filters)
                    .options(selectinload(UserVotingResult.extra_options))
                )
            )
            if (not user_voting_result or
                    (user_voting_result and
                     user_voting_result.is_voted_myself)):
                continue

            user_voting_result.vote = vote
            if extra_options:
                user_voting_result.extra_options = extra_options
            if noncompliance:
                user_voting_result.noncompliance = noncompliance

            await self._session.flush([user_voting_result])

            await self._propagate_vote(
                user_id=target_user_id,
                community_id=community_id,
                category_id=category_id,
                resource=resource,
                resource_type=resource_type,
                vote=vote,
                extra_options=extra_options,
                noncompliance=noncompliance,
            )


    async def _get_delegate_settings(
            self, user_id: str,
            community_id: str,
            category_id,
    ) -> List[DelegateSettings]:
        query = (
            select(DelegateSettings)
            .where(
                DelegateSettings.delegate_id == user_id,
                DelegateSettings.community_id == community_id,
                DelegateSettings.category_id == category_id,
            )
        )
        delegate_settings = await self._session.scalars(query)

        return list(delegate_settings)
