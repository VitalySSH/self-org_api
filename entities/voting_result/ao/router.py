from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from entities.community.ao.dataclasses import CsByPercent
from entities.voting_result.ao.dataclasses import SimpleVoteResult
from entities.voting_result.ao.datastorage import VotingResultDS

router = APIRouter()


@router.get(
    '/vote_in_percent/{result_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=SimpleVoteResult,
)
async def get_vote_in_percent(
    result_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> SimpleVoteResult:
    ds = VotingResultDS(session)

    return await ds.get_vote_in_percent(result_id)
