from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community.schemas import UpdateCommunity
from datastorage.crud.entities.status.schemas import ReadStatus, CreateStatus
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.database.base import get_async_session
from datastorage.database.models import Status
from datastorage.crud.schemas.list import Filters, Orders, Pagination, ListData


status_router = APIRouter()


@status_router.get(
    '/get/{status_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadStatus,
)
async def get_status(
    status_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ReadStatus:
    status_ds = CRUDDataStorage(model=Status, session=session)
    community: Status = await status_ds.get(status_id)
    if community:
        return status_ds.obj_to_schema(obj=community, schema=ReadStatus)
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=f'Статус с id: {status_id} не найден',
    )


@status_router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[ReadStatus],
)
async def list_status(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadStatus]:
    status_ds = CRUDDataStorage(model=Status, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    status_list: List[Status] = await status_ds.list(list_data)
    return [status_ds.obj_to_schema(obj=status, schema=ReadStatus)
            for status in status_list]


@status_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadStatus,
)
async def create_status(
    body: CreateStatus,
    session: AsyncSession = Depends(get_async_session),
) -> ReadStatus:
    status_ds = CRUDDataStorage(model=Status, session=session)
    status_to_add = status_ds.schema_to_obj(schema=body)
    try:
        new_status = await status_ds.create(status_to_add)
        return status_ds.obj_to_schema(obj=new_status, schema=ReadStatus)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@status_router.patch(
    '/update/{status_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_status(
    status_id: str,
    body: UpdateCommunity,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    status_ds = CRUDDataStorage(model=Status, session=session)
    try:
        await status_ds.update(obj_id=status_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@status_router.delete(
    '/update/{status_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_community_settings(
    status_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    status_ds = CRUDDataStorage(model=Status, session=session)
    try:
        await status_ds.delete(status_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
