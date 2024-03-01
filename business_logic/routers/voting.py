from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.dals.voting_dal import VotingDAL
from datastorage.database.base import get_async_session
from datastorage.interfaces import VotingParams, PercentByName

voting_router = APIRouter()


@voting_router.get(
    '/voting_settings/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def voting_settings(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> VotingParams:
    voting_dal = VotingDAL(session)
    return await voting_dal.calculate_voting_params(community_id)


@voting_router.get(
    '/community_names/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def community_names(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[str]:
    voting_dal = VotingDAL(session)
    return await voting_dal.get_all_community_names(community_id)


@voting_router.get(
    '/community_names_by_percen/{community_id}',
    dependencies=[Depends(auth_service.get_current_user)]
)
async def community_names_by_percen(
    community_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[PercentByName]:
    voting_dal = VotingDAL(session)
    return await voting_dal.get_voting_data_by_names(community_id)
