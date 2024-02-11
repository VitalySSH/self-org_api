import uuid

from fastapi_users import FastAPIUsers

from auth.auth import auth_backend
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserRead, UserCreate
from core.interfaces import IncludeRouter

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


def get_auth_router_data() -> IncludeRouter:
    return IncludeRouter(
        # router=fastapi_users.get_auth_router(auth_backend, requires_verification=True),
        router=fastapi_users.get_auth_router(auth_backend),
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
