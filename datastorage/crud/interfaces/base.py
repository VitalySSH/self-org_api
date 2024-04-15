import abc
from typing import TypeVar, Optional, Type, List, TypedDict, Any, Dict, Union

from sqlalchemy.orm import DeclarativeBase

from datastorage.crud.interfaces.list import Filters, Orders, Pagination

T = TypeVar('T', bound=DeclarativeBase)
S = TypeVar('S')


Include = List[str]


class RelationsSchema(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Any]


class SchemaReadInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    read_only: Dict[str, Any]
    relations: Dict[str, Union[RelationsSchema, List[RelationsSchema]]]


class SchemaInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Union[RelationsSchema, List[RelationsSchema]]]


class CRUD(abc.ABC):

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
