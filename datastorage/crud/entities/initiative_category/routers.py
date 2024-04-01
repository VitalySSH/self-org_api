from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.initiative_category.schemas import (
    InitCategoryRead, InitCategoryCreate, InitCategoryUpdate,
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.database.base import get_async_session
from datastorage.database.models import InitiativeCategory
from datastorage.crud.schemas.list import Filters, Orders, Pagination, ListData

ic_router = APIRouter()


@ic_router.get(
    '/get/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=InitCategoryRead,
)
async def get_initiative_category(
    ic_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> InitCategoryRead:
    ic_ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    ic: InitiativeCategory = await ic_ds.get(ic_id)
    if ic:
        return ic.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Настройки сообщества с id: {ic_id} не найдены',
    )


@ic_router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[InitCategoryRead],
)
async def list_initiative_category(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[InitCategoryRead]:
    ic_ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    ic_list: List[InitiativeCategory] = await ic_ds.list(list_data)
    return [ic.to_read_schema() for ic in ic_list]


@ic_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=InitCategoryRead,
)
async def create_initiative_category(
    body: InitCategoryCreate,
    session: AsyncSession = Depends(get_async_session),
) -> InitCategoryRead:
    ic_ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    ic_to_add: InitiativeCategory = await ic_ds.schema_to_model(schema=body)
    try:
        new_ic = await ic_ds.create(ic_to_add)
        return new_ic.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@ic_router.patch(
    '/update/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_initiative_category(
    ic_id: str,
    body: InitCategoryUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ic_ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    try:
        await ic_ds.update(obj_id=ic_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@ic_router.delete(
    '/update/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_initiative_category(
    ic_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ic_ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    try:
        await ic_ds.delete(ic_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
