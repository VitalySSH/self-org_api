import abc
from typing import Optional, Type, List, Callable

from datastorage.crud.dataclasses import PostProcessingData
from datastorage.crud.interfaces.list import Filters, Orders, Pagination
from datastorage.crud.interfaces.schema import S
from datastorage.interfaces import T


Include = Optional[List[str]]


class CRUD(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def get_relation_fields(schema: S) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def execute_post_processing(
            self, instance: Optional[T],
            post_processing_data: List[PostProcessingData],
            instance_id: Optional[str] = None,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def schema_to_model(self, schema: S) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(
            self, instance_id: str,
            include: Include = None,
            model: Type[T] = None
    ) -> Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, instance: T, relation_fields: Optional[List[str]] = None) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, instance_id: str, schema: S) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, instance_id: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(
            self, filters: Filters = None,
            orders: Orders = None,
            pagination: Pagination = None,
            include: Include = None,
    ) -> List[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def first(
            self, filters: Filters = None,
            orders: Orders = None,
            pagination: Pagination = None,
            include: Include = None,
    ) -> Optional[T]:
        raise NotImplementedError


class PostProcessing(abc.ABC):

    @abc.abstractmethod
    def execute(
            self, instance: Optional[T],
            post_processing_data: List[PostProcessingData],
            instance_id: Optional[str] = None,
    ) -> None:
        raise NotImplementedError

