from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from datastorage.interfaces import VotingParams, CsByPercent
from entities.community.ao.data_storage import CommunityDS
from entities.community.model import Community
from entities.community_description.crud.schemas import CommunityDescRead
from entities.community_name.crud.schemas import CommunityNameRead

router = APIRouter()


@router.get(
    '/voting_params/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def voting_settings(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> VotingParams:
    ds = CommunityDS(model=Community, session=session)
    return await ds.calculate_voting_params(community_id)


@router.get(
    '/names/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[CommunityNameRead],
)
async def community_names(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[CommunityNameRead]:
    ds = CommunityDS(model=Community, session=session)
    return await ds.get_community_names(community_id)


@router.get(
    '/descriptions/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[CommunityDescRead],
)
async def community_descriptions(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[CommunityDescRead]:
    ds = CommunityDS(model=Community, session=session)
    return await ds.get_community_descriptions(community_id)


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
    '/change_community_settings',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def change_community_settings(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = CommunityDS(model=Community, session=session)
    await ds.change_community_settings(community_id)
