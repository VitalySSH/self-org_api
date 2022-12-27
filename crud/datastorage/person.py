from typing import Optional, List

from uuid import uuid4

from databases.interfaces import Record

from crud.datasource.interfaces.list import Pagination, Filters, Orders
from crud.datastorage.implementations import DataStorageImpl
from crud.models.person import Person
from crud.database.tables import persons


class PersonDataStorage(DataStorageImpl):

    async def list(self, filters: Optional[Filters],
                   orders: Optional[Orders],
                   pagination: Optional[Pagination]) -> List[Record]:
        query = self.query_for_list(
            table=persons,
            filters=filters,
            orders=orders,
            pagination=pagination,
        )

        return await self.database.fetch_all(query)

    async def get(self, id: str) -> Optional[Person]:
        query = persons.select().where(persons.c.id == id).first()
        user = await self.database.fetch_one(query)
        return Person.parse_obj(user) if user else None

    async def create(self, person: Person) -> Person:
        if not person.id:
            person.id = str(uuid4())
        params = person.dict()
        query = persons.insert().values(**params)
        await self.database.execute(query)
        return Person.parse_obj(person)

    async def update(self, id: str, person: Person) -> Person:
        query = persons.update().where(persons.c.id == id).values(
            **person.dict())
        await self.database.execute(query)
        return Person.parse_obj(person)

    async def get_by_id(self, id: str) -> Person:
        query = persons.select().where(persons.c.id == id).first()
        user = await self.database.fetch_one(query)
        return Person.parse_obj(user) if user else None

    async def get_by_user_id(self, user_id: str) -> Person:
        query = persons.select().where(persons.c.user == user_id).first()
        user = await self.database.fetch_one(query)
        return Person.parse_obj(user) if user else None
