from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community.schemas import ReadCommunity, CreateCommunity, \
    UpdateCommunity
from datastorage.crud.exceptions import CRUDConflict, CRUDNotFound
from datastorage.database.base import get_async_session
from datastorage.models import Community
from datastorage.schemas.list import Filters, Orders, Pagination, ListData

community_router = APIRouter()


@community_router.get(
    '/get/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadCommunity,
)
async def get_community(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ReadCommunity:
    community_ds = CRUDDataStorage(model=Community, session=session)
    community: Community = await community_ds.get(community_id)
    if community:
        return community_ds.obj_with_relations_to_schema(obj=community, schema=ReadCommunity)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Пользователь с id: {community_id} не найден',
    )


@community_router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[ReadCommunity],
)
async def list_community(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadCommunity]:
    community_ds = CRUDDataStorage(model=Community, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    community_list: List[Community] = await community_ds.list(list_data)
    return [community_ds.obj_with_relations_to_schema(obj=cm, schema=ReadCommunity)
            for cm in community_list]


@community_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadCommunity,
)
async def create_community(
    body: CreateCommunity,
    session: AsyncSession = Depends(get_async_session),
) -> ReadCommunity:
    community_ds = CRUDDataStorage(model=Community, session=session)
    community_to_add = community_ds.schema_to_obj(schema=body)
    try:
        new_community = await community_ds.create(community_to_add)
        return community_ds.obj_with_relations_to_schema(obj=new_community, schema=ReadCommunity)
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
    body: UpdateCommunity,
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
