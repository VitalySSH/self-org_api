from typing import Optional, Type

from fastapi import Response, Request, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from auth.interfaces import AuthService, TokenService, TokenDelivery
from auth.services.user_service import UserService
from core.config import COOKIE_TOKEN_NAME
from datastorage.database.base import get_async_session
from datastorage.database.models import User


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthUserService(AuthService):
    """Сервис аутентификации."""

    _token_service: TokenService
    _token_delivery: TokenDelivery
    _user_service_cls: Type[UserService]

    def __init__(
            self,
            token_service: TokenService,
            token_delivery: TokenDelivery,
    ):
        self._token_service = token_service
        self._token_delivery = token_delivery
        self._user_service_cls = UserService

    def create_user_service(self, session: AsyncSession) -> UserService:
        return self._user_service_cls(session)

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
        """Получение текущего пользователя по токену."""
        user: Optional[User] = None
        token = request.cookies.get(COOKIE_TOKEN_NAME)
        if token:
            decoded_token = self._token_service.decode_token(token)
            user_id = decoded_token.get('sub')
            user_service = self.create_user_service(session)
            user = await user_service.get_user_by_id(user_id)
        if user:
            return user

        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
