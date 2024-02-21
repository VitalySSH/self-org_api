from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from auth.user.schemas import ReadUser, CreateUser
from datastorage.crud.dataclasses import ListData
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.base import get_async_session
from datastorage.interfaces.list import Filters, Orders, Pagination
from datastorage.models import User

user_router = APIRouter()


@user_router.get(
    "/get/{user_id}",
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ReadUser,
)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ReadUser:
    user_ds = CRUDDataStorage(model=User, session=session)
    user = await user_ds.get(user_id)
    if user:
        return user_ds.obj_to_schema(obj=user, schema=ReadUser)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Пользователь с id: {user_id} не найден',
    )


@user_router.post('/list', response_model=List[ReadUser])
async def get_users(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadUser]:
    user_ds = CRUDDataStorage(model=User, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    users = await user_ds.list(list_data)
    return [user_ds.obj_to_schema(obj=user, schema=ReadUser) for user in users]


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
    return user_ds.obj_to_schema(obj=new_user, schema=ReadUser)

