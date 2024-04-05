from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community_settings.schemas import (
    CreateComSettings, ReadComSettings, updateComSettings
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.database.base import get_async_session
from datastorage.database.models import CommunitySettings
from datastorage.crud.schemas.list import Filters, Orders, Pagination, ListData

cs_router = APIRouter()


@cs_router.get(
    '/get/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadComSettings,
)
async def get_community_settings(
    cs_id: str,
    include: List[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> ReadComSettings:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    cs: CommunitySettings = await cs_ds.get(obj_id=cs_id, include=include)
    if cs:
        return cs.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Настройки сообщества с id: {cs_id} не найдены',
    )


@cs_router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[ReadComSettings],
)
async def list_community_settings(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadComSettings]:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    cs_list: List[CommunitySettings] = await cs_ds.list(list_data)
    return [cs.to_read_schema() for cs in cs_list]


@cs_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadComSettings,
)
async def create_community_settings(
    body: CreateComSettings,
    session: AsyncSession = Depends(get_async_session),
) -> ReadComSettings:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    cs_to_add: CommunitySettings = await cs_ds.schema_to_model(schema=body)
    try:
        new_cs = await cs_ds.create(cs_to_add)
        return new_cs.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@cs_router.patch(
    '/update/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_community_settings(
    cs_id: str,
    body: updateComSettings,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    try:
        await cs_ds.update(obj_id=cs_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@cs_router.delete(
    '/update/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_community_settings(
    cs_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    try:
        await cs_ds.delete(cs_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
