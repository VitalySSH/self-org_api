from typing import cast

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from auth.user.schemas import ReadUser, CreateUser
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.base import get_async_session
from datastorage.models import User

user_router = APIRouter()


@user_router.post("/create", response_model=ReadUser)
async def create_user(
        body: CreateUser,
        session: AsyncSession = Depends(get_async_session),
) -> ReadUser:
    user_ds = CRUDDataStorage(model=User, session=session)
    body.password = auth_service.get_password_hash(body.password)
    mapping = {'password': 'hashed_password'}
    user_to_add = user_ds.schema_to_obj(schema=body, mapping=mapping)
    new_user = await user_ds.create(user_to_add)
    return user_ds.obj_to_schema(schema=ReadUser, obj=new_user)

