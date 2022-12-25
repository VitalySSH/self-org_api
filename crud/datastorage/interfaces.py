from typing import Optional, List

from databases.interfaces import Record

from crud.datasource.interfaces.list import Object, Orders, Filters, Pagination


class Datastorage:

    async def list(self, filters: Optional[Filters],
                   orders: Optional[Orders],
                   pagination: Optional[Pagination]) -> List[Record]:
        raise NotImplementedError

    async def get(self, id: str) -> Object:
        raise NotImplementedError

    async def create(self, obj: object) -> Object:
        raise NotImplementedError

    async def update(self, id: str, obj: object) -> Object:
        raise NotImplementedError
