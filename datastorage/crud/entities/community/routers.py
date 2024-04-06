from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community.schemas import CommunityRead, CommunityCreate, \
    CommunityUpdate

from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.crud.schemas.interfaces import Include
from datastorage.database.base import get_async_session
from datastorage.database.models import Community
from datastorage.crud.schemas.list import Filters, Orders, Pagination

community_router = APIRouter()


@community_router.get(
    '/get/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=CommunityRead,
)
async def get_community(
    community_id: str,
    include: Include = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> CommunityRead:
    community_ds = CRUDDataStorage(model=Community, session=session)
    community: Community = await community_ds.get(obj_id=community_id, include=include)
    if community:
        return community.to_read_schema()
    raise HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=f'Сообщество с id: {community_id} не найдено',
    )


@community_router.post(
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
    community_ds = CRUDDataStorage(model=Community, session=session)
    community_list: List[Community] = await community_ds.list(
        filters=filters, orders=orders, pagination=pagination, include=include)
    return [community.to_read_schema() for community in community_list]


@community_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=CommunityRead,
)
async def create_community(
    body: CommunityCreate,
    session: AsyncSession = Depends(get_async_session),
) -> CommunityRead:
    community_ds = CRUDDataStorage(model=Community, session=session)
    community_to_add: Community = await community_ds.schema_to_model(schema=body)
    try:
        new_community = await community_ds.create(community_to_add)
        return new_community.to_read_schema()
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@community_router.patch(
    '/update/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_community(
    community_id: str,
    body: CommunityUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    community_ds = CRUDDataStorage(model=Community, session=session)
    try:
        await community_ds.update(obj_id=community_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@community_router.delete(
    '/update/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_community_settings(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    community_ds = CRUDDataStorage(model=Community, session=session)
    try:
        await community_ds.delete(community_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
