from typing import Literal, Optional

from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT

from auth.interfaces import TokenDelivery
from core import config
from core.config import COOKIE_TOKEN_NAME

SamesiteType = Literal['lax', 'strict', 'none']


class CookieTokenDelivery(TokenDelivery):
    _name: str
    _max_age: Optional[int]
    _path: str
    _domain: Optional[str]
    _secure: bool
    _httponly: bool
    _samesite: SamesiteType

    def __init__(
        self,
        name: str = COOKIE_TOKEN_NAME,
        max_age: int = config.JWT_LIFE_TIME_SECONDS,
        path: str = '/',
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SamesiteType = 'lax',
    ):
        self._name = name
        self._max_age = max_age
        self._path = path
        self._domain = domain
        self._secure = secure
        self._httponly = httponly
        self._samesite = samesite

    def login_response(self, token: str) -> Response:
        response = Response(status_code=HTTP_204_NO_CONTENT)
        response.set_cookie(
            key=self._name,
            value=token.decode() if isinstance(token, bytes) else token,
            max_age=self._max_age,
            path=self._path,
            domain=self._domain,
            secure=self._secure,
            httponly=self._httponly,
            samesite=self._samesite,
        )

        return response

    def logout_response(self) -> Response:
        response = Response(status_code=HTTP_204_NO_CONTENT)
        response.set_cookie(
            key=self._name,
            value='',
            max_age=0,
            path=self._path,
            domain=self._domain,
            secure=self._secure,
            httponly=self._httponly,
            samesite=self._samesite,
        )
        return response
