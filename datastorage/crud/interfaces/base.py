import abc
from typing import TypeVar, Optional, Type, List, TypedDict, Any, Dict, Union

from sqlalchemy.orm import DeclarativeBase

from datastorage.crud.interfaces.list import Filters, Orders, Pagination
from datastorage.interfaces import SchemaInstanceAbstract

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

    @staticmethod
    @abc.abstractmethod
    def get_relation_fields(schema: SchemaInstanceAbstract) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    async def schema_to_model(self, schema: SchemaInstanceAbstract) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(
            self, instance_id: str,
            include: Optional[Include] = None,
            model: Type[T] = None
    ) -> Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, instance: T, relation_fields: Optional[List[str]] = None) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, instance_id: str, schema: SchemaInstance) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, instance_id: str) -> None:
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
