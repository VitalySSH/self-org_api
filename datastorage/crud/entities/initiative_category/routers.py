from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.initiative_category.schemas import (
    InitCategoryRead, InitCategoryCreate, InitCategoryUpdate,
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import InitiativeCategory
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=InitCategoryRead,
)
async def get_initiative_category(
    obj_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> InitCategoryRead:
    ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    ic: InitiativeCategory = await ds.get(obj_id=obj_id, include=include)
    if ic:
        return ic.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Категория инициативы с id: {obj_id} не найдена',
    )


@router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[InitCategoryRead],
)
async def list_initiative_category(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[InitCategoryRead]:
    ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    ic_list: List[InitiativeCategory] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [ic.to_read_schema() for ic in ic_list]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=InitCategoryRead,
)
async def create_initiative_category(
    body: InitCategoryCreate,
    session: AsyncSession = Depends(get_async_session),
) -> InitCategoryRead:
    ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    ic_to_add: InitiativeCategory = await ds.schema_to_model(schema=body)
    try:
        new_init_category = await ds.create(ic_to_add)
        return new_init_category.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_initiative_category(
    obj_id: str,
    body: InitCategoryUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/{initiative_category_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_initiative_category(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=InitiativeCategory, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
