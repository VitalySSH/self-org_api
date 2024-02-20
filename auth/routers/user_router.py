from typing import cast, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from auth.user.schemas import ReadUser, CreateUser
from datastorage.crud.dataclasses import ListData
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.base import get_async_session
from datastorage.interfaces.list import Filters, Orders, Pagination
from datastorage.models import User

user_router = APIRouter()


@user_router.get("/get/{user_id}", response_model=ReadUser)
async def create_user(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> ReadUser:
    user_ds = CRUDDataStorage(model=User, read_schema=ReadUser, session=session)
    user = await user_ds.get(user_id)
    return user_ds.obj_to_schema(obj=user)


@user_router.post('/list', response_model=List[ReadUser])
async def get_users(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadUser]:
    user_ds = CRUDDataStorage(model=User, read_schema=ReadUser, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    users = await user_ds.list(list_data)
    return users


@user_router.post("/create", response_model=ReadUser)
async def create_user(
    body: CreateUser,
    session: AsyncSession = Depends(get_async_session),
) -> ReadUser:
    user_ds = CRUDDataStorage(model=User, read_schema=ReadUser, session=session)
    body.password = auth_service.get_password_hash(body.password)
    mapping = {'password': 'hashed_password'}
    user_to_add = user_ds.schema_to_obj(schema=body, mapping=mapping)
    new_user = await user_ds.create(user_to_add)
    return user_ds.obj_to_schema(obj=new_user)

