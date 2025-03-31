from datetime import datetime
from typing import List, Optional

from datastorage.ao.datastorage import AODataStorage
from datastorage.consts import Code
from sqlalchemy import select

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.utils import build_uuid
from entities.category.model import Category
from entities.initiative.ao.dataclasses import CreatingNewInitiative
from entities.initiative.model import Initiative
from entities.status.model import Status
from auth.models.user import User
from entities.user_community_settings.model import UserCommunitySettings
from entities.user_voting_result.model import UserVotingResult
from entities.voting_option.model import VotingOption
from entities.voting_result.model import VotingResult


class InitiativeDS(AODataStorage[Initiative], CRUDDataStorage):

    _model = Initiative

    async def create_initiative(
            self, data: CreatingNewInitiative,
            creator: User
    ) -> None:
        """Создаст новую инициативу."""
        initiative_id = build_uuid()
        is_multi_select = data.get('is_multi_select') or False
        voting_result: VotingResult = await self._create_voting_result()
        event_date_str = data.get('event_date')
        event_date: Optional[datetime] = None
        if event_date_str:
            event_date = datetime.fromisoformat(event_date_str).today()
        initiative = self.__class__._model()
        initiative.id = initiative_id
        initiative.title = data.get('title')
        initiative.question = data.get('question')
        initiative.content = data.get('content')
        initiative.is_one_day_event = data.get('is_one_day_event')
        initiative.event_date = event_date
        initiative.is_extra_options = data.get('is_extra_options') or False
        initiative.is_multi_select = is_multi_select
        initiative.community_id = data.get('community_id')
        initiative.extra_question = data.get('extra_question')
        initiative.creator = creator
        initiative.responsible = creator
        initiative.voting_result = voting_result
        initiative.status = await self.get_status_by_code(
            Code.ON_CONSIDERATION
        )
        initiative.category = await self.get(
            instance_id=data.get('category_id'), model=Category)
        extra_options = await self._create_options(
            option_values=data.get('extra_options') or [],
            is_multi_select=is_multi_select,
            creator_id=creator.id,
            initiative_id=initiative_id,
        )

        try:
            self._session.add(initiative)
            await self._session.flush([initiative])
            await self._session.refresh(initiative)
            await self._create_user_results(
                initiative=initiative,
                voting_result=voting_result,
                extra_options=extra_options,
                creator_id=creator.id,
            )
            await self._session.commit()
        except Exception as e:
            raise Exception(f'Не удалось создать правило: {e.__str__()}')

    async def get_status_by_code(self, code: str) -> Optional[Status]:
        status_query = select(Status).where(Status.code == code)

        return await self._session.scalar(status_query)

    async def _create_options(
            self, option_values: List[str],
            creator_id: str,
            is_multi_select: bool,
            initiative_id: str,
    ) -> List[VotingOption]:
        options: List[VotingOption] = []
        for option_value in option_values:
            option = VotingOption()
            option.content = option_value
            option.is_multi_select = is_multi_select
            option.creator_id = creator_id
            option.initiative_id = initiative_id
            try:
                self._session.add(option)
                options.append(option)
            except Exception as e:
                raise Exception(
                    f'Не удалось создать опцию для правила: {e.__str__()}'
                )

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
                f'Не удалось создать результат '
                f'голосования для правила: {e.__str__()}'
                )

        return voting_result

    async def _create_user_results(
            self, initiative: Initiative,
            voting_result: VotingResult,
            extra_options: List[VotingOption],
            creator_id: str,
    ) -> None:
        user_cs_query = (
            select(
                UserCommunitySettings.user_id,
                UserCommunitySettings.is_blocked,
            ).where(
                UserCommunitySettings.community_id == initiative.community_id
            )
        )
        user_cs_data = await self._session.execute(user_cs_query)
        user_cs_list = user_cs_data.all()

        for user_id, is_blocked in user_cs_list:
            user_voting_result = UserVotingResult()
            user_voting_result.voting_result = voting_result
            user_voting_result.member_id = user_id
            user_voting_result.community_id = initiative.community_id
            user_voting_result.initiative_id = initiative.id
            user_voting_result.is_blocked = is_blocked
            if user_id == creator_id:
                user_voting_result.extra_options = extra_options
            self._session.add(user_voting_result)
