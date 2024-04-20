from dataclasses import dataclass
from typing import List, Callable, Dict, Any, Type, Optional

from datastorage.base import DataStorage
from datastorage.crud.enum import Method
from datastorage.interfaces import T


@dataclass
class PostProcessingSettings:
    methods: List[Method]
    func_name: str
    instance_attr: str


@dataclass
class PostProcessingData:
    data_storage: Type[DataStorage]
    model: Type[T]
    settings: PostProcessingSettings
    include: Optional[List[str]] = None


@dataclass
class ThreadFuncData:
    func: Callable
    kwargs: Dict[str, Any]


@dataclass
class InitPostProcessing:
    instance: T
    method: Method
    post_processing_data: PostProcessingData
