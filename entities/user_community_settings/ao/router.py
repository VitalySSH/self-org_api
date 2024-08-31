from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.database.base import get_async_session
from entities.user_community_settings.ao.datastorage import UserCommunitySettingsDS
from entities.user_community_settings.model import UserCommunitySettings

router = APIRouter()


@router.post(
    '/update_data_after_join',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=201,
)
async def add_request_member(
        user_settings_id: str,
        community_id: str,
        request_member_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    ds = UserCommunitySettingsDS(model=UserCommunitySettings, session=session)
    await ds.update_data_after_join(
        user_settings_id=user_settings_id,
        community_id=community_id,
        request_member_id=request_member_id,
    )
