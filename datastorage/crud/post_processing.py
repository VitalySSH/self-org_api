import asyncio
from asyncio import Task
from threading import Thread
from typing import Optional, List, Set

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import ThreadFuncData, PostProcessingData
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T


class CRUDPostProcessing(Thread, PostProcessing):
    """Постобработка запросов со стороны клиента."""

    post_processing_data: List[PostProcessingData]
    _instance: Optional[T]
    _background_tasks: Set[Task]

    def __init__(self):
        super().__init__()
        self._background_tasks = set()

    def run(self) -> None:
        funcs_data = self._build_func_data(self._instance)
        task = asyncio.create_task(self._execute_functions(funcs_data))
        self._background_tasks.add(task)
        task.add_done_callback(lambda _task: self._background_tasks.remove(_task))

    def execute(self, instance: T, post_processing_data: List[PostProcessingData]) -> None:
        self._instance = instance
        self.post_processing_data = post_processing_data
        self.run()

    @staticmethod
    async def _execute_functions(funcs_data: List[ThreadFuncData]):
        for func_data in funcs_data:
            await func_data.func(**func_data.kwargs)

    def _build_func_data(self, instance: T) -> List[ThreadFuncData]:
        funcs_data: List[ThreadFuncData] = []
        for post_processing in self.post_processing_data:
            ds: DataStorage = self._init_data_storage(post_processing)
            func = getattr(ds, post_processing.func_name)
            if post_processing.instance_attr:
                attr_value = getattr(instance, post_processing.instance_attr)
            else:
                attr_value = instance
            if func and attr_value:
                attrs = list(func.__annotations__.keys())
                if attrs:
                    kwargs = {attrs[0]: attr_value}
                    funcs_data.append(ThreadFuncData(func=func, kwargs=kwargs))
                else:
                    funcs_data.append(ThreadFuncData(func=func, kwargs={}))

        return funcs_data

    @staticmethod
    def _init_data_storage(post_processing: PostProcessingData) -> DataStorage:
        ds_class = post_processing.data_storage

        return ds_class(model=post_processing.model)
