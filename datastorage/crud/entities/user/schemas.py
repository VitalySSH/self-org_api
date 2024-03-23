import re
from datetime import datetime
from typing import Union, TypedDict

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, EmailStr

from datastorage.crud.schemas.base import DirtyAttribute, dirty_attribute, BaseUpdateScheme

LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')


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
    email: str
    is_active: bool
    created: datetime


class UserRead(TypedDict):
    id: str
    attributes: UserReadAttributes


class UserCreateAttributes(TypedDict):
    firstname: str
    surname: str
    email: str
    is_active: bool
    hashed_password: str


class UserCreate(TypedDict, total=False):
    id: str
    attributes: UserCreateAttributes


class BaseUser(BaseModel):
    firstname: str
    surname: str
    email: EmailStr
    is_active: bool


class ReadUser(BaseUser):
    id: str
    created: datetime

    class Config:
        from_attributes = True


class CreateUser(BaseUser, ValidateMixin):
    hashed_password: str


class UpdateUser(BaseUpdateScheme, ValidateMixin):
    firstname: Union[str, DirtyAttribute] = dirty_attribute
    surname: Union[str, DirtyAttribute] = dirty_attribute
    email: Union[EmailStr, DirtyAttribute] = dirty_attribute
    is_active: Union[bool, DirtyAttribute] = dirty_attribute
    hashed_password: Union[str, DirtyAttribute] = dirty_attribute
