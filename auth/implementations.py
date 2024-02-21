from typing import Optional, Type, TypeVar

from fastapi import Response, Request, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from auth.interfaces import Auth, Token, TokenDelivery
from auth.token.delivery.cookie import COOKIE_TOKEN_NAME
from datastorage.database.base import get_async_session
from datastorage.models import User

DS = TypeVar('DS')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService(Auth):
    """Сервис аутентификации."""

    _token_service: Token
    _token_delivery: TokenDelivery
    _datastorage: Type[DS]

    def __init__(
            self,
            token_service: Token,
            token_delivery: TokenDelivery,
            datastorage: Type[DS]
    ):
        self._token_service = token_service
        self._token_delivery = token_delivery
        self._datastorage = datastorage

    async def access_token(self, user_id: str) -> Response:
        token = self._token_service.create_access_token(user_id)
        return self._token_delivery.login_response(token)

    async def clean_token(self) -> Response:
        return self._token_delivery.logout_response()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def get_current_user(
            self, request: Request,
            session: AsyncSession = Depends(get_async_session)) -> User:
        user: Optional[User] = None
        token = request.cookies.get(COOKIE_TOKEN_NAME)
        if token:
            user_ds = self._datastorage(session=session, model=User)
            decoded_token = self._token_service.decode_token(token)
            user_id = decoded_token.get('sub')
            user = await user_ds.get(user_id)
        if user:
            return user
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
