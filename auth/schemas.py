from typing import Optional, TypedDict

from pydantic import BaseModel


class BaseUser(BaseModel):
    firstname: str
    surname: str
    email: str
    about_me: Optional[str] = None


class CurrentUser(BaseUser):
    id: str
    foto_id: Optional[str]


class UserCreate(BaseUser):
    secret_password: str


class UserUpdate(TypedDict, total=False):
    firstname: str
    surname: str
    email: str
    about_me: Optional[str]
    foto_id: Optional[str]
