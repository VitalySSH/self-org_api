from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.auth import auth_service
from auth.dataclasses import CreateUserResult
from auth.schemas import (
    CurrentUser, UserCreate, UserUpdate, CreateUserResponse, ListUserSchema,
    ReadUser
)
from auth.security import decrypt_password, verify_password
from auth.services.user_service import UserService
from datastorage.crud.dataclasses import ListResponse
from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Filters, Orders, Pagination, \
    Filter, Operation
from datastorage.database.base import get_async_session
from datastorage.database.models import User, UserData

auth_router = APIRouter()


@auth_router.post('/login', status_code=204)
async def login_for_access_token(
        email: EmailStr = Form(), secret_password: str = Form(),
        session: AsyncSession = Depends(get_async_session),
):
    user_service: UserService = auth_service.create_user_service(session)
    user: Optional[User] = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь с email: {email} не найден',
        )

    user_data: UserData = await user_service.get_user_data_by_user_id(user.id)
    password = decrypt_password(secret_password)
    if not verify_password(
            password=password, 
            hashed_password=user_data.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Введён некорректный email или пароль',
        )

    return await auth_service.access_token(user.id)


@auth_router.post('/logout', status_code=204)
async def clean_token():
    return await auth_service.clean_token()


@auth_router.get(
    '/user/me',
    response_model=CurrentUser,
    status_code=200,
)
async def get_current_user(
        current_user: User = Depends(auth_service.get_current_user),
):
    return CurrentUser(
        id=current_user.id,
        firstname=current_user.firstname,
        surname=current_user.surname,
        fullname=current_user.fullname,
        about_me=current_user.about_me,
        foto_id=current_user.foto_id,
        email=current_user.email,
    )


@auth_router.post(
    '/user/list',
    dependencies=[Depends(auth_service.get_current_user)],
    response_model=ListUserSchema,
    status_code=200,
)
async def list_users(
        filters: Filters = None,
        orders: Orders = None,
        pagination: Pagination = None,
        include: Include = None,
        session: AsyncSession = Depends(get_async_session),
) -> ListUserSchema:
    ds = CRUDDataStorage[User](model=User, session=session)
    resp: ListResponse[User] = await ds.list(
        filters=filters, orders=orders,
        pagination=pagination, include=include
    )

    return ListUserSchema(
        items=[
            ReadUser(
                id=user.id,
                fullname=user.fullname,
                firstname=user.firstname,
                surname=user.surname,
                about_me=user.about_me,
                foto_id=user.foto_id,
            )
            for user in resp.data
        ],
        total=resp.total
    )


@auth_router.post(
    '/user/list/{community_id}',
    response_model=ListUserSchema,
    status_code=200,
)
async def list_users(
        community_id: str,
        filters: Filters = None,
        orders: Orders = None,
        pagination: Pagination = None,
        include: Include = None,
        is_delegates: bool = False,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_async_session),
) -> ListUserSchema:
    user_service: UserService = auth_service.create_user_service(session)
    ds = CRUDDataStorage[User](model=User, session=session)
    user_ids = await user_service.get_user_ids_from_community(
        community_id=community_id,
        is_delegates=is_delegates,
        current_user_id=current_user.id,
    )
    if filters is None:
        filters = []
    filters.append(Filter(field='id', op=Operation.IN, val=user_ids))

    resp: ListResponse[User] = await ds.list(
        filters=filters, orders=orders,
        pagination=pagination, include=include
    )

    return ListUserSchema(
        items=[
            ReadUser(
                id=user.id,
                fullname=user.fullname,
                firstname=user.firstname,
                surname=user.surname,
                about_me=user.about_me,
                foto_id=user.foto_id,
            )
            for user in resp.data
        ],
        total=resp.total
    )


@auth_router.post('/user')
async def create_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session),
) -> CreateUserResponse:
    user_service: UserService = auth_service.create_user_service(session)
    result: CreateUserResult = await user_service.create_user(user_data)
    match result.status_code:
        case 201:
            return {'ok': result.message}
        case 409:
            return {'error': result.message}
        case 500:
            return {'error': result.message}


@auth_router.patch(
    '/user/{user_id}',
    status_code=204,
)
async def update_user(
        user_id: str,
        user_data: UserUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    user_service: UserService = auth_service.create_user_service(session)
    await user_service.update_user(user_id=user_id, user_data=user_data)
