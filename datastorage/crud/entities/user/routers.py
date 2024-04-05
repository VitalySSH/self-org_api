from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_service
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.entities.user.schemas import UserCreate, UserRead, UserUpdate
from datastorage.crud.exceptions import CRUDNotFound, CRUDConflict
from datastorage.database.base import get_async_session
from datastorage.crud.schemas.list import Filters, Orders, Pagination, ListData
from datastorage.database.models import User

user_router = APIRouter()


@user_router.get(
    '/get/{user_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=UserRead,
)
async def get_user(
    user_id: str,
    include: List[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    user_ds = CRUDDataStorage(model=User, session=session)
    user: User = await user_ds.get(obj_id=user_id, include=include)
    if user:
        return user.to_read_schema()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Пользователь с id: {user_id} не найден',
    )


@user_router.post(
    '/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=List[UserRead],
)
async def list_users(
    filters: Optional[Filters] = None,
    orders: Optional[Orders] = None,
    pagination: Optional[Pagination] = None,
    session: AsyncSession = Depends(get_async_session),
) -> List[UserRead]:
    user_ds = CRUDDataStorage(model=User, session=session)
    list_data = ListData(filters=filters, orders=orders, pagination=pagination)
    users: List[User] = await user_ds.list(list_data)
    return [user.to_read_schema() for user in users]


@user_router.post(
    '/create',
    response_model=UserRead,
)
async def create_user(
    body: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    user_ds = CRUDDataStorage(model=User, session=session)
    user_to_add: User = await user_ds.schema_to_model(schema=body)
    new_user = await user_ds.create(user_to_add)
    return new_user.to_read_schema()


@user_router.patch(
    '/update/{user_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def update_user(
    user_id: str,
    body: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    user_ds = CRUDDataStorage(model=User, session=session)
    try:
        await user_ds.update(obj_id=user_id, schema=body)
    except CRUDNotFound as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )


@user_router.delete(
    '/update/{user_id}',
    dependencies=[Depends(auth_service.get_current_user)],
    status_code=204,
)
async def delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    user_ds = CRUDDataStorage(model=User, session=session)
    try:
        await user_ds.delete(user_id)
    except CRUDConflict as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.description,
        )
