from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community.schemas import (
    CommunityRead, CommunityCreate, CommunityUpdate
)
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import Community
from datastorage.crud.schemas.list import Filters, Orders, Pagination

router = APIRouter()


@router.get(
    '/get/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=CommunityRead,
)
async def get_community(
    obj_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> CommunityRead:
    ds = CRUDDataStorage(model=Community, session=session)
    community: Community = await ds.get(obj_id=obj_id, include=include)
    if community:
        return community.to_read_schema()
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=f'Сообщество с id: {obj_id} не найдено',
    )


@router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[CommunityRead],
)
async def list_community(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    include: Optional[Include] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[CommunityRead]:
    ds = CRUDDataStorage(model=Community, session=session)
    community_list: List[Community] = await ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [community.to_read_schema() for community in community_list]


@router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=CommunityRead,
)
async def create_community(
    body: CommunityCreate,
    session: AsyncSession = Depends(get_async_session),
) -> CommunityRead:
    ds = CRUDDataStorage(model=Community, session=session)
    community_to_add: Community = await ds.schema_to_model(schema=body)
    try:
        new_community = await ds.create(community_to_add)
        return new_community.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.patch(
    '/update/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_community(
    obj_id: str,
    body: CommunityUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Community, session=session)
    try:
        await ds.update(obj_id=obj_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@router.delete(
    '/update/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_community(
    obj_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CRUDDataStorage(model=Community, session=session)
    try:
        await ds.delete(obj_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
