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
    instance_attr: str
    include: Optional[List[str]] = None


@dataclass
class ThreadFuncData:
    func: Callable
    kwargs: Dict[str, Any]


@dataclass
class InitPostProcessing:
    instance: T
    post_processing_data: PostProcessingData
