from typing import Optional, List

from uuid import uuid4

from databases.interfaces import Record

from core.security import hash_password
from crud.datasource.interfaces.list import Pagination, Filters, Orders
from crud.datastorage.implementations import DataStorageImpl
from crud.models.user import User
from crud.database.tables import users


class UserDataStorage(DataStorageImpl):

    async def list(self, filters: Optional[Filters],
                   orders: Optional[Orders],
                   pagination: Optional[Pagination]) -> List[Record]:
        query = self.query_for_list(
            table=users,
            filters=filters,
            orders=orders,
            pagination=pagination,
        )

        return await self.database.fetch_all(query)

    async def get(self, id: str) -> Optional[User]:
        query = users.select().where(users.c.id == id).first()
        user = await self.database.fetch_one(query)
        return User.parse_obj(user) if user else None

    async def create(self, user: User) -> User:
        if not user.id:
            user.id = str(uuid4())
        params = user.dict()
        query = users.insert().values(**params)
        await self.database.execute(query)
        if user.password:
            user.password = '********'
        return User.parse_obj(user)

    async def update(self, id: str, user_data: User) -> User:
        user = User(
            id=id,
            email=user_data.email,
            phone=user_data.phone,
            password=(
                hash_password(user_data.password) if
                type(user_data.password) != hash else user_data.password),
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
