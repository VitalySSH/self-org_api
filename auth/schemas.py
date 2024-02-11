import uuid
from datetime import datetime

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    second_name: str
    created: datetime


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    second_name: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    second_name: str
