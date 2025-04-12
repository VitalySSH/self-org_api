from fastapi import APIRouter, Depends

from auth.auth import auth_service
from auth.models.user import User
from entities.user_community_settings.ao.dataclasses import CreatingCommunity
from entities.user_community_settings.ao.datastorage import UserCommunitySettingsDS
from entities.user_community_settings.ao.schemas import (
    SettingDataToCreate, ChildSettingDataToCreate
)
from entities.user_community_settings.crud.schemas import UserCsAttributes, UserCsRead

router = APIRouter()


@router.post(
    '/create_community',
    status_code=201,
)
async def create_new_community(
        settings: SettingDataToCreate,
        user: User = Depends(auth_service.get_current_user),
) -> None:
    ds = UserCommunitySettingsDS()
    async with ds.session_scope():
        user = await ds.merge_into_session(user)
        try:
            names = settings.pop('names')
            descriptions = settings.pop('descriptions')
            category_names = []
            if settings.get('categories'):
                categories = settings.pop('categories')
                category_names = list(
                    map(lambda it: it.get('name'), categories)
                )
            data_to_create = CreatingCommunity(
                names=names,
                descriptions=descriptions,
                category_names=category_names,
                settings=UserCsAttributes(**settings),
                user=user,
            )
            await ds.create_community(data_to_create)
        except KeyError as key:
            raise Exception(
                f'Ошибка входных данных, '
                f'параметр settings не содержит поля {key}'
            )
        except Exception as e:
            raise Exception(f'Ошибка создания сообщества: {e.__str__()}')


@router.post(
    '/create_child_settings',
    response_model=UserCsRead,
    status_code=201,
)
async def create_child_settings(
        settings: ChildSettingDataToCreate,
        user: User = Depends(auth_service.get_current_user),
) -> UserCsRead:
    ds = UserCommunitySettingsDS()
    async with ds.session_scope():
        user = await ds.merge_into_session(user)

        try:
            names = settings.pop('names')
            descriptions = settings.pop('descriptions')
            parent_community_id = settings.pop('parent_community_id')
            category_names = []
            if settings.get('categories'):
                categories = settings.pop('categories')
                category_names = list(
                    map(lambda it: it.get('name'), categories)
                )
            data_to_create = CreatingCommunity(
                names=names,
                descriptions=descriptions,
                category_names=category_names,
                settings=UserCsAttributes(**settings),
                user=user,
                parent_community_id=parent_community_id,
            )
            child_settings = await ds.create_child_settings(data_to_create)

            return child_settings.to_read_schema()
        except KeyError as key:
            raise Exception(
                f'Ошибка входных данных,'
                f' параметр settings не содержит поля {key}'
            )
        except Exception as e:
            raise Exception(
                f'Ошибка создания пользовательских настроек '
                f'для внутреннего сообщества: {e.__str__()}'
            )
