import abc
from fastapi import Response, Request
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
    async def access_token(self, user_id: str) -> Response:
        raise NotImplementedError

    async def clean_token(self) -> Response:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_password_hash(password: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_current_user(self, request: Request) -> User:
        raise NotImplementedError
