import jwt
from datetime import timedelta, datetime
from typing import Optional


from auth.interfaces import TokenService
from core import config

JWT_ALGORITHM = 'HS256'


class JWTTokenService(TokenService):
    """Логика для работы с JWT токеном."""

    _secret_key: str
    _expires_seconds: int
    _algorithm: str

    def __init__(
            self,
            secret_key: str = config.JWT_SECRET_KEY,
            expires_seconds: int = config.JWT_LIFE_TIME_SECONDS,
            algorithm: str = JWT_ALGORITHM,
    ):
        self._secret_key = secret_key
        self._expires_seconds = expires_seconds
        self._algorithm = algorithm

    def create_access_token(self, user_id: str) -> str:
        payload = {'sub': user_id}

        return self._generate_token(payload=payload)

    def _generate_token(
            self,
            payload: dict,
            expires_delta: Optional[timedelta] = None,
    ) -> str:
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(seconds=self._expires_seconds)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            payload=to_encode,
            key=self._secret_key,
            algorithm=self._algorithm,
        )
        if isinstance(encoded_jwt, bytes):
            encoded_jwt = encoded_jwt.decode()

        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        return jwt.decode(jwt=token, key=self._secret_key, algorithms=[self._algorithm])
