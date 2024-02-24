from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.community_settings.schemas import (
    ReadCS, CreateCS
)
from datastorage.database.base import get_async_session
from datastorage.models import CommunitySettings, User

cs_router = APIRouter()


@cs_router.get(
    '/get/{community_settings_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadCS,
)
async def get_community_settings(
    cs_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ReadCS:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    cs: CommunitySettings = await cs_ds.get(cs_id)
    if cs:
        return cs_ds.obj_to_schema(obj=cs, schema=ReadCS)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Пользователь с id: {cs_id} не найден',
    )


@cs_router.post(
    '/create',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadCS,
)
async def create_community_settings(
    body: CreateCS,
    session: AsyncSession = Depends(get_async_session),
) -> ReadCS:
    cs_ds = CRUDDataStorage(model=CommunitySettings, session=session)
    cs_to_add = cs_ds.schema_to_obj(schema=body)
    new_cs = await cs_ds.create(cs_to_add)
    return cs_ds.obj_to_schema(obj=new_cs, schema=ReadCS)
