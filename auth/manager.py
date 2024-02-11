from typing import Optional, Any

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidID

from app.core.config import PASSWORD_SECRET_KEY
from app.datastorage.database.base import get_user_db
from auth.models import User


class IdMixin:
    def parse_id(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        try:
            return str(value)
        except ValueError as e:
            raise InvalidID() from e


class UserManager(IdMixin, BaseUserManager[User, str]):
    reset_password_token_secret = PASSWORD_SECRET_KEY
    verification_token_secret = PASSWORD_SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f'User {user.id} has registered.')

    # async def on_after_forgot_password(
    #     self, user: User, token: str, request: Optional[Request] = None
    # ):
    #     print(f'User {user.id} has forgot their password. Reset token: {token}')
    #
    # async def on_after_request_verify(
    #     self, user: User, token: str, request: Optional[Request] = None
    # ):
    #     print(f'Verification requested for user {user.id}. Verification token: {token}')


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
