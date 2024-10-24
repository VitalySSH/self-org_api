import abc
from fastapi import Response, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services.user_service import UserService
from datastorage.database.base import get_async_session
from datastorage.database.models import User


class TokenDelivery(abc.ABC):
    """Доставка токена клиенту."""

    @abc.abstractmethod
    def login_response(self, token: str) -> Response:
        raise NotImplementedError

    @abc.abstractmethod
    def logout_response(self) -> Response:
        raise NotImplementedError


class TokenService(abc.ABC):
    """Логика для работы с токеном."""

    @abc.abstractmethod
    def create_access_token(self, user_id: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def decode_token(self, token: str) -> dict:
        raise NotImplementedError


class AuthService(abc.ABC):
    """Аутентификация."""

    @abc.abstractmethod
    def create_user_service(self, session: AsyncSession) -> UserService:
        raise NotImplementedError

    @abc.abstractmethod
    async def access_token(self, user_id: str) -> Response:
        raise NotImplementedError

    async def clean_token(self) -> Response:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_password_hash(password: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_current_user(
            self, request: Request,
            session: AsyncSession = Depends(get_async_session)) -> User:
        raise NotImplementedError
