import re

from fastapi import HTTPException
from pydantic import BaseModel, field_validator, EmailStr, constr

LETTER_MATCH_PATTERN = re.compile(r'^[а-яА-Яa-zA-Z\-]+$')


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class BaseUser(BaseModel):
    firstname: str
    surname: str
    email: EmailStr
    is_active: bool


class ReadUser(BaseUser):
    id: str

    class Config:
        orm_mode = True


class CreateUser(BaseUser):
    password: constr(min_length=8)

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
