from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from entities.request_member.ao.data_storage import RequestMemberDS
from entities.request_member.model import RequestMember

router = APIRouter()


@router.post(
    '/add_to_community_settings',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def add_request_member(
    request_member_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = RequestMemberDS(model=RequestMember, session=session)
    await ds.add_request_member(request_member_id)
