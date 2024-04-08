from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community_settings.schemas import (
    CreateComSettings, ReadComSettings, UpdateComSettings
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import CommunitySettings
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadComSettings,
)
async def get_community_settings(
    obj_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> ReadComSettings:
    ds = CRUDDataStorage(model=CommunitySettings, session=session)
    obj: CommunitySettings = await ds.get(obj_id=obj_id, include=include)
    if obj:
        return obj.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Настройки сообщества с id: {obj_id} не найдены',
    )


@router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[ReadComSettings],
)
async def list_community_settings(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadComSettings]:
    ds = CRUDDataStorage(model=CommunitySettings, session=session)
    obj_list: List[CommunitySettings] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [obj.to_read_schema() for obj in obj_list]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadComSettings,
)
async def create_community_settings(
    body: CreateComSettings,
    session: AsyncSession = Depends(get_async_session),
) -> ReadComSettings:
    ds = CRUDDataStorage(model=CommunitySettings, session=session)
    obj_to_add: CommunitySettings = await ds.schema_to_model(schema=body)
    try:
        new_obj = await ds.create(obj_to_add)
        return new_obj.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/update/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_community_settings(
    obj_id: str,
    body: UpdateComSettings,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=CommunitySettings, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/update/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_community_settings(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=CommunitySettings, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
