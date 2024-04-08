from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.delegate_settings.schemas import (
    DelegateSettingsRead, DelegateSettingsCreate, DelegateSettingsUpdate
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import DelegateSettings
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=DelegateSettingsRead,
)
async def get_community_settings(
    obj_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> DelegateSettingsRead:
    ds = CRUDDataStorage(model=DelegateSettings, session=session)
    obj: DelegateSettings = await ds.get(obj_id=obj_id, include=include)
    if obj:
        return obj.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Настройки сообщества с id: {obj_id} не найдены',
    )


@router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[DelegateSettingsRead],
)
async def list_community_settings(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[DelegateSettingsRead]:
    ds = CRUDDataStorage(model=DelegateSettings, session=session)
    obj_list: List[DelegateSettings] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [obj.to_read_schema() for obj in obj_list]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=DelegateSettingsRead,
)
async def create_community_settings(
    body: DelegateSettingsCreate,
    session: AsyncSession = Depends(get_async_session),
) -> DelegateSettingsRead:
    ds = CRUDDataStorage(model=DelegateSettings, session=session)
    obj_to_add: DelegateSettings = await ds.schema_to_model(schema=body)
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
    body: DelegateSettingsUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=DelegateSettings, session=session)
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
    ds = CRUDDataStorage(model=DelegateSettings, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
