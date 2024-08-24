from dataclasses import dataclass
from typing import List, Callable, Dict, Any, Type, Optional

from datastorage.base import DataStorage
from datastorage.crud.enum import Method
from datastorage.interfaces import T


@dataclass
class PostProcessingData:
    data_storage: Type[DataStorage]
    model: Type[T]
    methods: List[Method]
    func_name: str
    instance_attr: Optional[str] = None
    include: Optional[List[str]] = None


@dataclass
class TaskFuncData:
    func: Callable
    kwargs: Dict[str, Any]
