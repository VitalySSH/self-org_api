from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.opinion.schemas import OpinionRead, OpinionUpdate, OpinionCreate
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.crud.utils import update_object_by_likes
from datastorage.database.base import get_async_session
from datastorage.database.models import User, Opinion
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{opinion_id}',
    response_model=OpinionRead,
)
async def get_opinion(
    obj_id: str,
    include: Include = Query(None),
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> OpinionRead:
    ds = CRUDDataStorage(model=Opinion, session=session)
    opinion: Opinion = await ds.get(obj_id=obj_id, include=include)
    if opinion:
        return update_object_by_likes(obj=opinion, current_user=current_user)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Инициатива с id: {obj_id} не найдена',
    )


@router.post(
    '/list',
    response_model=List[OpinionRead],
)
async def list_opinion(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[OpinionRead]:
    ds = CRUDDataStorage(model=Opinion, session=session)
    opinions: List[Opinion] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)

    return [update_object_by_likes(obj=opinion, current_user=current_user)
            for opinion in opinions]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=OpinionRead,
)
async def create_opinion(
    body: OpinionCreate,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> OpinionRead:
    ds = CRUDDataStorage(model=Opinion, session=session)
    opinion_to_add: Opinion = await ds.schema_to_model(schema=body)
    try:
        new_opinion = await ds.create(opinion_to_add)
        return update_object_by_likes(obj=new_opinion, current_user=current_user)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/update/{opinion_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_opinion(
    obj_id: str,
    body: OpinionUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Opinion, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/update/{opinion_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_opinion(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Opinion, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
