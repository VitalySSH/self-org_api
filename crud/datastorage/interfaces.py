from typing import List

from crud.datasource.interfaces.list import Object


class Datastorage:

    async def list(self, filters: List[dict], pagination) -> List[Object]:
        raise NotImplementedError

    async def get(self, id: str) -> Object:
        raise NotImplementedError

    async def create(self) -> Object:
        raise NotImplementedError

    async def update(self):
        raise NotImplementedError
