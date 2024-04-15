from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from datastorage.interfaces import VotingParams, PercentByName
from entities.community.ao.ao import CommunityDS
from entities.community.model import Community

router = APIRouter()


@router.get(
    '/main_voting_settings/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def voting_settings(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> VotingParams:
    ds = CommunityDS(model=Community, session=session)
    return await ds.calculate_voting_params(community_id)


@router.get(
    '/community_names/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def community_names(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[str]:
    ds = CommunityDS(model=Community, session=session)
    return await ds.get_all_community_names(community_id)


@router.get(
    '/community_names_by_percen/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def community_names_by_percen(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[PercentByName]:
    ds = CommunityDS(model=Community, session=session)
    return await ds.get_voting_data_by_names(community_id)


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
