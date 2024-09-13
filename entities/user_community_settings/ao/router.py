from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from entities.user.model import User
from entities.user_community_settings.ao.dataclasses import CreatingCommunity
from entities.user_community_settings.ao.datastorage import UserCommunitySettingsDS
from entities.user_community_settings.ao.schemas import SettingDataToCreate
from entities.user_community_settings.crud.schemas import UserCsAttributes
from entities.user_community_settings.model import UserCommunitySettings

router = APIRouter()


@router.post(
    '/update_data_after_join',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=201,
)
async def add_request_member(
        user_settings_id: str,
        community_id: str,
        request_member_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = UserCommunitySettingsDS(model=UserCommunitySettings, session=session)
    await ds.update_data_after_join(
        user_settings_id=user_settings_id,
        community_id=community_id,
        request_member_id=request_member_id,
    )


@router.post(
    '/create_community',
    status_code=201,
)
async def create_new_community(
        settings: SettingDataToCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(auth_service.get_current_user),
) -> None:
    ds = UserCommunitySettingsDS(model=UserCommunitySettings, session=session)
    try:
        name = settings.pop('name')
        description = settings.pop('description')
        categories = settings.pop('categories')
        init_categories = list(map(lambda it: it.get('name'), categories))
        data_to_create = CreatingCommunity(
            name=name,
            description=description,
            init_categories=init_categories,
            settings=UserCsAttributes(**settings),
            user=user
        )
        await ds.create_community(data_to_create)
    except KeyError as key:
        raise Exception(f'Ошибка входных данных, параметр settings не содержит поля {key}')
    except Exception as e:
        raise Exception(f'Ошибка создания сообщества: {e}')
