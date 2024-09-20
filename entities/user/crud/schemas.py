import re
from datetime import datetime
from typing import TypedDict, Optional

from fastapi import HTTPException
from pydantic import field_validator

LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')


# TODO: Сделать валидацию
class ValidateMixin:

    @classmethod
    @field_validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Имя должно состоять только из букв'
            )
        return value

    @classmethod
    @field_validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Фамилия должна состоять только из букв'
            )
        return value


class UserReadAttributes(TypedDict):
    firstname: str
    surname: str
    about_me: Optional[str]
    foto_id: Optional[str]
    email: str
    is_active: bool
    created: datetime


class UserRead(TypedDict):
    id: str
    attributes: UserReadAttributes


class UserCreateAttributes(TypedDict, total=False):
    firstname: str
    surname: str
    about_me: Optional[str]
    foto_id: Optional[str]
    email: str
    is_active: bool
    hashed_password: str


class UserCreate(TypedDict, total=False):
    id: str
    attributes: UserCreateAttributes


class UserUpdate(UserCreate):
    pass
