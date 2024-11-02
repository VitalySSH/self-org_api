from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from core.dataclasses import PercentByName
from datastorage.database.base import get_async_session
from entities.community.model import Community
from entities.request_member.ao.datastorage import RequestMemberDS

router = APIRouter()


@router.get(
    '/votes_in_percen/{request_member_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[PercentByName],
    status_code=200,
)
async def votes_in_percen(
    request_member_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[PercentByName]:
    ds = RequestMemberDS(model=Community, session=session)

    return await ds.get_request_member_in_percent(request_member_id)
