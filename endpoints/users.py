import json
from typing import Optional, List

from fastapi import APIRouter, Depends

from crud.datasource.interfaces.list import Filters, Pagination, Orders
from crud.models.user import User
from crud.datastorage.users import UserDataStorage
from endpoints.depends import get_user_datastorage

router = APIRouter()


@router.post('/list', response_model=List[User])
async def get_users(
        users: UserDataStorage = Depends(get_user_datastorage),
        filters: Optional[Filters] = None,
        orders: Optional[Orders] = None,
        pagination: Optional[Pagination] = None):
    return await users.list(
        filters=filters,
        orders=orders,
        pagination=pagination,
    )


@router.post('/', response_model=User)
async def create(user: User,
                 users: UserDataStorage = Depends(get_user_datastorage)):
    return await users.create(user)


@router.put('/', response_model=User)
async def update(id: str, user: User,
                 users: UserDataStorage = Depends(get_user_datastorage)):
    return await users.update(id, user)
