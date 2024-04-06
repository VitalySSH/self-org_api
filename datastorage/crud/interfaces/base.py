import abc
from typing import TypeVar, Optional, Type, List

from datastorage.crud.schemas.interfaces import Include
from datastorage.crud.schemas.list import ListData, Filters, Orders, Pagination
from datastorage.interfaces import SchemaInstance

T = TypeVar('T')
S = TypeVar('S')


class DataStorage(abc.ABC):

    @abc.abstractmethod
    async def schema_to_model(self, schema: SchemaInstance, model: Type[T] = None) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(
            self, obj_id: str,
            include: Optional[Include] = None,
            model: Type[T] = None
    ) -> Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, obj: T) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, obj_id: str, schema: S) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, obj_id: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(
            self, filters: Optional[Filters] = None,
            orders: Optional[Orders] = None,
            pagination: Optional[Pagination] = None,
            include: Optional[Include] = None,
    ) -> List[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def first(
            self, filters: Optional[Filters] = None,
            orders: Optional[Orders] = None,
            pagination: Optional[Pagination] = None,
            include: Optional[Include] = None,
    ) -> Optional[T]:
        raise NotImplementedError
