from dataclasses import dataclass
from typing import List, Callable, Dict, Any, Type, Optional, Generic, TypeVar

from datastorage.ao.base import AODataStorage
from datastorage.crud.enum import Method


Instance = TypeVar('Instance')


@dataclass
class PostProcessingData:
    data_storage: Type[AODataStorage]
    methods: List[Method]
    func_name: str
    instance_attr: Optional[str] = None
    include: Optional[List[str]] = None


@dataclass
class TaskFuncData:
    func: Callable
    kwargs: Dict[str, Any]


@dataclass
class ListResponse(Generic[Instance]):
    data: List[Instance]
    total: int
