from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.initiative.schemas import (
    InitiativeRead, InitiativeCreate, InitiativeUpdate,
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.crud.utils import update_object_by_likes
from datastorage.database.base import get_async_session
from datastorage.database.models import User, Initiative
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{initiative_id}',
    response_model=InitiativeRead,
)
async def get_initiative(
    obj_id: str,
    include: Include = Query(None),
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> InitiativeRead:
    ds = CRUDDataStorage(model=Initiative, session=session)
    initiative: Initiative = await ds.get(obj_id=obj_id, include=include)
    if initiative:
        return update_object_by_likes(obj=initiative, current_user=current_user)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Инициатива с id: {obj_id} не найдена',
    )


@router.post(
    '/list',
    response_model=List[InitiativeRead],
)
async def list_initiative(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[InitiativeRead]:
    ds = CRUDDataStorage(model=Initiative, session=session)
    initiatives: List[Initiative] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)

    return [update_object_by_likes(obj=initiative, current_user=current_user)
            for initiative in initiatives]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=InitiativeRead,
)
async def create_initiative(
    body: InitiativeCreate,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> InitiativeRead:
    ds = CRUDDataStorage(model=Initiative, session=session)
    initiative_to_add: Initiative = await ds.schema_to_model(schema=body)
    try:
        new_initiative = await ds.create(initiative_to_add)
        return update_object_by_likes(obj=new_initiative, current_user=current_user)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/update/{initiative_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_initiative(
    obj_id: str,
    body: InitiativeUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Initiative, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/update/{initiative_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_initiative(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Initiative, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
