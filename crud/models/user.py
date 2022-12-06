from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator, constr


class User(BaseModel):
    id: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    password: Optional[constr(min_length=8)]
    password_2: Optional[str]
    created: Optional[datetime]
    is_active: Optional[bool]

    @validator('password_2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
