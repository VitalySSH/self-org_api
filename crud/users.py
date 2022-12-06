from datetime import datetime
from typing import List, Optional

from uuid import uuid4

from core.security import hash_password
from crud.datasource.interfaces.list import Pagination, Filters, Orders
from crud.models.user import User, UserIn, UserUpdate
from crud.base import BaseDataStorage
from crud.database.tables import users


class UserDataStorage(BaseDataStorage):

    async def list(self, filters: Optional[Filters] = None,
                   order: Optional[Orders] = None,
                   pagination: Optional[Pagination] = None) -> List[User]:
        _limit = pagination.get('limit') if pagination else 20
        _skip = pagination.get('skip') if pagination else 1
        query = users.select().limit(_limit).offset(_skip)
        return await self.database.fetch_all(query)

    async def get(self, id: str) -> Optional[User]:
        query = users.select().where(users.c.id == id).first()
        user = await self.database.fetch_one(query)
        return User.parse_obj(user) if user else None

    async def create(self, user_data: UserIn) -> User:
        user = User(
            id=user_data.id or uuid4().hex,
            name=user_data.name,
            surname=user_data.surname,
            second_name=user_data.second_name,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=hash_password(user_data.password),
            created=datetime.now(),
        )

        query = users.insert().values(**user.dict())
        await self.database.execute(query)
        user.hashed_password = '******'
        return User.parse_obj(user)

    async def update(self, id: str, user_data: UserUpdate) -> User:
        user = User(
            id=id,
            name=user_data.name,
            surname=user_data.surname,
            second_name=user_data.second_name,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=(hash_password(user_data.password)
                             if type(user_data.password) != hash
                             else user_data.password),
        )

        query = users.update().where(users.c.id == id).values(**user.dict())
        await self.database.execute(query)
        return User.parse_obj(user)

    async def get_by_email(self, email: str) -> User:
        query = users.select().where(users.c.email == email).first()
        user = await self.database.fetch_one(query)
        return User.parse_obj(user) if user else None

    async def get_by_phone(self, phone: str) -> User:
        query = users.select().where(users.c.phone == phone).first()
        user = await self.database.fetch_one(query)
        return User.parse_obj(user) if user else None
