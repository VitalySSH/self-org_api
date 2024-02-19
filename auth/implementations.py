from fastapi import Response
from passlib.context import CryptContext

from auth.interfaces import Auth, Token, TokenDelivery

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthService(Auth):
    """Сервис аутентификации."""

    _token_service: Token
    _token_delivery: TokenDelivery

    def __init__(self, token_service: Token, token_delivery: TokenDelivery) -> None:
        self._token_service = token_service
        self._token_delivery = token_delivery

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
