from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from auth.models.user import User
from core.dataclasses import PercentByName
from datastorage.database.base import get_async_session
from entities.request_member.ao.dataclasses import MyMemberRequest
from entities.request_member.ao.datastorage import RequestMemberDS

router = APIRouter()


@router.get(
    '/votes_in_percent/{request_member_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[PercentByName],
    status_code=200,
)
async def votes_in_percent(
    request_member_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[PercentByName]:
    ds = RequestMemberDS(session)

    return await ds.get_request_member_in_percent(request_member_id)


@router.post(
    '/add_new_member/{request_member_id}',
    status_code=204,
)
async def add_new_member(
    request_member_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> None:
    ds = RequestMemberDS(session)
    await ds.add_new_member(
        request_member_id=request_member_id,
        current_user=current_user
    )


@router.get(
    '/my_list',
    status_code=200,
    response_model=List[MyMemberRequest]
)
async def my_list(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[MyMemberRequest]:
    ds = RequestMemberDS(session)

    return await ds.my_list(current_user.id)
