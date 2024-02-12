import uuid
from typing import List

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_backend
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserRead, UserCreate, UserUpdate
from core.interfaces import IncludeRouter
from datastorage.database.base import get_async_session
from datastorage.database.tables import user

user_router = APIRouter()

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


def get_auth_router_data() -> IncludeRouter:
    return IncludeRouter(
        router=fastapi_users.get_auth_router(backend=auth_backend, requires_verification=True),
        prefix='/auth/jwt',
        tags=['auth'],
    )


def get_register_router_data() -> IncludeRouter:
    return IncludeRouter(
        router=fastapi_users.get_register_router(
            user_schema=UserRead, user_create_schema=UserCreate),
        prefix='/auth/jwt',
        tags=['auth'],
    )


def get_user_router_data() -> IncludeRouter:
    return IncludeRouter(
        router=fastapi_users.get_users_router(
            user_schema=UserRead, user_update_schema=UserUpdate, requires_verification=True),
        prefix='/users',
        tags=['users'],
    )


@user_router.post('/list')
async def get_users(session: AsyncSession = Depends(get_async_session)):
    users = await session.execute(select(user))
    return [UserRead(**user_._mapping) for user_ in users.all()]
