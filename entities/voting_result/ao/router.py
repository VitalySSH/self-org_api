from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from entities.voting_result.ao.dataclasses import SimpleVoteInPercent
from entities.voting_result.ao.datastorage import VotingResultDS

router = APIRouter()


@router.get(
    '/vote_in_percent/{result_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=SimpleVoteInPercent,
)
async def get_vote_in_percent(
    result_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> SimpleVoteInPercent:
    ds = VotingResultDS(session)
    result = await ds.get_vote_in_percent(result_id)

    return asdict(result)
