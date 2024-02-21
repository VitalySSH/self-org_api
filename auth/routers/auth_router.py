from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from auth.user.schemas import LoginUserSchema
from datastorage.crud.dataclasses import ListData
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.database.base import get_async_session
from datastorage.interfaces.list import Filter, Operation
from datastorage.models import User

auth_router = APIRouter()


@auth_router.post('/login')
async def login_for_access_token(
    login_user: LoginUserSchema,
    session: AsyncSession = Depends(get_async_session),
):
    user_ds = CRUDDataStorage(model=User, session=session)
    filters = [Filter(field='email', op=Operation.EQ, val=login_user.email)]
    list_data = ListData(filters=filters)
    user = await user_ds.first(list_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с email: {login_user.email} не найден',
        )
    if not auth_service.verify_password(
            password=login_user.password, hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Введён некорректный email или пароль',
        )

    return await auth_service.access_token(user.id)


@auth_router.post('/logout')
async def login_for_access_token():
    return await auth_service.clean_token()
