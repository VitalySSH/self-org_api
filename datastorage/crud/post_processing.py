from fastapi import BackgroundTasks
from typing import Optional, List

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import TaskFuncData, PostProcessingData
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T


class CRUDPostProcessing(PostProcessing):
    """Постобработка запросов со стороны клиента."""

    post_processing_data: List[PostProcessingData]
    _instance: Optional[T]
    _background_tasks: BackgroundTasks

    def __init__(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks

    def execute(self, instance: T, post_processing_data: List[PostProcessingData]) -> None:
        if self._background_tasks:
            self._instance = instance
            self.post_processing_data = post_processing_data
            funcs_data = self._build_func_data(self._instance)
            self._background_tasks.add_task(self._execute_functions, *funcs_data)

    @staticmethod
    async def _execute_functions(*funcs_data):
        for func_data in funcs_data:
            await func_data.func(**func_data.kwargs)

    def _build_func_data(self, instance: T) -> List[TaskFuncData]:
        funcs_data: List[TaskFuncData] = []
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
                    funcs_data.append(TaskFuncData(func=func, kwargs=kwargs))
                else:
                    funcs_data.append(TaskFuncData(func=func, kwargs={}))

        return funcs_data

    @staticmethod
    def _init_data_storage(post_processing: PostProcessingData) -> DataStorage:
        ds_class = post_processing.data_storage

        return ds_class(model=post_processing.model)
