import abc
from typing import TypeVar, Optional, Dict, Type

T = TypeVar('T')
S = TypeVar('S')
RS = TypeVar('RS')


class DataStorage(abc.ABC):

    @abc.abstractmethod
    def schema_to_obj(self, schema: S,
                      mapping: Optional[Dict[str, str]] = None) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def obj_to_schema(self, obj: T,
                      mapping: Optional[Dict[str, str]] = None) -> RS:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, obj_id: str) -> Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, obj: T) -> T:
        raise NotImplementedError
