from typing import List, Optional
from datastorage.consts import Code
from sqlalchemy import select
from datastorage.crud.datastorage import CRUDDataStorage
from entities.category.model import Category
from entities.opinion.model import Opinion
from entities.rule.ao.dataclasses import CreatingNewRule
from entities.rule.model import Rule
from entities.status.model import Status
from auth.models.user import User
from entities.voting_result.model import VotingResult


class RuleDS(CRUDDataStorage[Rule]):

    async def create_rule(self, data: CreatingNewRule, creator: User) -> None:
        """Создаст новое правило."""
        rule = Rule()
        rule.title = data.get('title')
        rule.question = data.get('question')
        rule.content = data.get('content')
        rule.is_extra_options = data.get('is_extra_options') or False
        rule.is_multi_select = data.get('is_multi_select') or False
        rule.community_id = data.get('community_id')
        rule.creator = creator
        rule.voting_result = await self._create_voting_result()
        rule.status = await self._get_status_by_code(Code.ON_CONSIDERATION)
        rule.category = await self.get(instance_id=data.get('category_id'), model=Category)
        rule.opinions = await self._create_options(
            option_values=data.get('extra_options') or [], creator_id=creator.id)
        try:
            self._session.add(rule)
            await self._session.commit()
        except Exception as e:
            raise Exception(f'Не удалось создать правило: {e}')

    async def _get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def _create_options(self, option_values: List[str], creator_id: str) -> List[Opinion]:
        options: List[Opinion] = []
        for option_value in option_values:
            option = Opinion()
            option.creator_id = creator_id
            option.text = option_value
            try:
                self._session.add(option)
                await self._session.flush([option])
                await self._session.refresh(option)
            except Exception as e:
                raise Exception(f'Не удалось создать опцию для правила: {e}')
            options.append(option)

        return options

    async def _create_voting_result(self) -> VotingResult:
        voting_result = VotingResult()
        try:
            self._session.add(voting_result)
            await self._session.flush([voting_result])
            await self._session.refresh(voting_result)
        except Exception as e:
            raise Exception(f'Не удалось создать результат голосования для правила: {e}')

        return voting_result
