from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator, constr


class User(BaseModel):
    uuid: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    second_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    hashed_password: Optional[str]
    created: Optional[datetime]


class UserIn(BaseModel):
    name: str
    surname: str
    second_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    password: constr(min_length=8)
    password_2: str

    @validator('password_2')
    def password_match(cls, password2, fields, **kwargs):
        if 'password' in fields and password2 != fields.get('password'):
            raise ValueError('passwords don\'t match')

        return password2
