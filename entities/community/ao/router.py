from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Filters, Orders, Pagination, Filter, Operation
from datastorage.crud.interfaces.schema import ListResponseSchema
from datastorage.database.base import get_async_session
from entities.community.ao.dataclasses import CsByPercent, CommunityNameData, SubCommunityData
from entities.community.ao.datastorage import CommunityDS
from entities.community.crud.schemas import CommunityRead
from auth.models.user import User

router = APIRouter()


@router.get(
    '/settings_in_percent/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=CsByPercent,
)
async def community_settings_by_percent(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> CsByPercent:
    ds = CommunityDS(session)

    return await ds.get_community_settings_in_percent(community_id)


@router.get(
    '/name/{community_id}',
    response_model=CommunityNameData,
)
async def get_community_name_data(
    community_id: str,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> CommunityNameData:
    ds = CommunityDS(session)

    return await ds.get_community_name_data(community_id=community_id, user_id=current_user.id)


@router.get(
    '/sub_communities/{community_id}',
    response_model=List[SubCommunityData],
)
async def get_sub_communities_data(
    community_id: str,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[SubCommunityData]:
    ds = CommunityDS(session)

    return await ds.get_sub_community_data(community_id=community_id, user_id=current_user.id)


@router.post(
    '/my_list',
    response_model=ListResponseSchema[CommunityRead],  # type: ignore
    status_code=200,
)
async def my_list(
    filters: Filters = None,
    orders: Orders = None,
    pagination: Pagination = None,
    include: Include = None,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> ListResponseSchema[CommunityRead]:  # type: ignore
    ao_ds = CommunityDS(session)
    communities_ids = await ao_ds.get_current_user_community_ids(current_user.id)
    my_filters: Filters = [
        Filter(field='id', op=Operation.IN, val=communities_ids),
        Filter(field='parent_id', op=Operation.NULL, val=False),
    ]
    if filters:
        my_filters += filters

    resp = await ao_ds.list(
        filters=my_filters, orders=orders, pagination=pagination, include=include)

    return ListResponseSchema[CommunityRead](  # type: ignore
        items=[instance.to_read_schema() for instance in resp.data],
        total=resp.total
    )
