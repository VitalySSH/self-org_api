from typing import Optional, TypedDict, List

from pydantic import BaseModel

from datastorage.crud.interfaces.base import Include
from datastorage.crud.interfaces.list import Pagination, Filters, Orders


class BaseUser(BaseModel):
    firstname: str
    surname: str
    email: str
    about_me: Optional[str] = None


class ReadUser(TypedDict):
    id: str
    fullname: str
    firstname: str
    surname: str
    about_me: Optional[str]
    foto_id: Optional[str]


class ListUserSchema(TypedDict):
    items: List[ReadUser]
    total: int


class CurrentUser(BaseUser):
    id: str
    fullname: str
    foto_id: Optional[str]


class UserCreate(BaseUser):
    secret_password: str


class UserUpdate(TypedDict, total=False):
    firstname: str
    surname: str
    email: str
    about_me: Optional[str]
    foto_id: Optional[str]


class ListUsers(TypedDict, total=False):
    filters: Filters
    orders: Orders
    pagination: Pagination
    include: Include
    is_delegates: bool


class CreateUserResponse(TypedDict, total=False):
    ok: str
    error: str
