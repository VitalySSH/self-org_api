from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Filters, Orders, Pagination, Filter, Operation
from datastorage.database.base import get_async_session
from entities.community.ao.dataclasses import CsByPercent
from entities.community.ao.datastorage import CommunityDS
from entities.community.crud.schemas import CommunityRead
from entities.community.model import Community
from auth.models.user import User

router = APIRouter()


@router.get(
    '/settings_in_percen/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def community_settings_by_percen(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> CsByPercent:
    ds = CommunityDS(model=Community, session=session)

    return await ds.get_community_settings_in_percent(community_id)


@router.post(
    '/my_list',
    response_model=List[CommunityRead],
    status_code=200,
)
async def my_list(
    filters: Filters = None,
    orders: Orders = None,
    pagination: Pagination = None,
    include: Include = None,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[Community]:
    ao_ds = CommunityDS(model=Community, session=session)
    communities_ids = await ao_ds.get_current_user_community_ids(current_user)
    my_filters: Filters = [Filter(field='id', op=Operation.IN, val=communities_ids)]
    if filters:
        my_filters += filters

    communities: List[Community] = await ao_ds.list(
        filters=my_filters, orders=orders, pagination=pagination, include=include)

    return [community.to_read_schema() for community in communities]
