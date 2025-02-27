from typing import List, Optional

from datastorage.ao.base import AODataStorage
from datastorage.consts import Code
from sqlalchemy import select

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.utils import build_uuid
from entities.category.model import Category
from entities.rule.ao.dataclasses import CreatingNewRule
from entities.rule.model import Rule
from entities.status.model import Status
from auth.models.user import User
from entities.user_community_settings.model import UserCommunitySettings
from entities.user_voting_result.model import UserVotingResult
from entities.voting_option.model import VotingOption
from entities.voting_result.model import VotingResult


class RuleDS(AODataStorage[Rule], CRUDDataStorage):

    _model = Rule

    async def create_rule(self, data: CreatingNewRule, creator: User) -> None:
        """Создаст новое правило."""
        rule_id = build_uuid()
        is_multi_select = data.get('is_multi_select') or False
        rule = self.__class__._model()
        rule.id = rule_id
        rule.title = data.get('title')
        rule.question = data.get('question')
        rule.content = data.get('content')
        rule.is_extra_options = data.get('is_extra_options') or False
        rule.is_multi_select = is_multi_select
        rule.community_id = data.get('community_id')
        rule.extra_question = data.get('extra_question')
        rule.creator = creator
        rule.voting_result = await self._create_voting_result()
        rule.status = await self.get_status_by_code(Code.ON_CONSIDERATION)
        rule.category = await self.get(
            instance_id=data.get('category_id'), model=Category)
        extra_options = await self._create_options(
            option_values=data.get('extra_options') or [],
            is_multi_select=is_multi_select,
            creator_id=creator.id,
            rule_id=rule_id,
        )

        try:
            self._session.add(rule)
            await self._session.flush([rule])
            await self._session.refresh(rule)
            await self._create_user_results(
                rule=rule,
                extra_options=extra_options,
                creator_id=creator.id,
            )
            await self._session.commit()
        except Exception as e:
            raise Exception(f'Не удалось создать правило: {e}')

    async def get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def _create_options(
            self, option_values: List[str],
            creator_id: str,
            is_multi_select: bool,
            rule_id: str,
    ) -> List[VotingOption]:
        options: List[VotingOption] = []
        for option_value in option_values:
            option = VotingOption()
            option.content = option_value
            option.is_multi_select = is_multi_select
            option.creator_id = creator_id
            option.rule_id = rule_id
            try:
                self._session.add(option)
                options.append(option)
            except Exception as e:
                raise Exception(f'Не удалось создать опцию для правила: {e}')

        await self._session.flush(options)

        return options

    async def _create_voting_result(self) -> VotingResult:
        voting_result = VotingResult()
        try:
            self._session.add(voting_result)
            await self._session.flush([voting_result])
            await self._session.refresh(voting_result)
        except Exception as e:
            raise Exception(
                f'Не удалось создать результат голосования для правила: {e}')

        return voting_result

    async def _create_user_results(
            self, rule: Rule,
            extra_options: List[VotingOption],
            creator_id: str,
    ) -> None:
        user_cs_query = (
            select(
                UserCommunitySettings.user_id,
                UserCommunitySettings.is_blocked,
            ).where(UserCommunitySettings.community_id == rule.community_id)
        )
        user_cs_data = await self._session.execute(user_cs_query)
        user_cs_list = user_cs_data.all()

        for user_id, is_blocked in user_cs_list:
            voting_result = UserVotingResult()
            voting_result.voting_result_id = rule.voting_result_id
            voting_result.member_id = user_id
            voting_result.community_id = rule.community_id
            voting_result.rule_id = rule.id
            voting_result.is_blocked = is_blocked
            if user_id == creator_id:
                voting_result.extra_options = extra_options
            self._session.add(voting_result)
