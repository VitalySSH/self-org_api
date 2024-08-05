import asyncio
from threading import Thread
from typing import Optional, Callable

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import ThreadFuncData, PostProcessingData
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T


class CRUDPostProcessing(Thread, PostProcessing):
    """Постобработка запросов со стороны клиента."""

    _post_processing: PostProcessingData
    _instance: Optional[T]
    _invalidate_session_func: Callable

    def run(self) -> None:
        background_tasks = []
        invalidate_session_task = asyncio.create_task(self._invalidate_session_func())
        background_tasks.append(invalidate_session_task)
        func_data = self._build_func_data(self._instance)
        if func_data:
            task = asyncio.create_task(func_data.func(**func_data.kwargs))
            background_tasks.append(task)

        while len(background_tasks) > 0:
            task_ = background_tasks[0]
            background_tasks.remove(task_)

    def execute(
            self, instance: T,
            post_processing_data: PostProcessingData,
            invalidate_session_func: Callable,
    ) -> None:
        self._instance = instance
        self._invalidate_session_func = invalidate_session_func
        self._post_processing = post_processing_data
        self.run()

    def _build_func_data(self, instance: T) -> Optional[ThreadFuncData]:
        ds: DataStorage = self._init_data_storage()
        func_data: Optional[ThreadFuncData] = None
        func = getattr(ds, self._post_processing.func_name)
        if self._post_processing.instance_attr:
            attr_value = getattr(instance, self._post_processing.instance_attr)
        else:
            attr_value = instance
        if func and attr_value:
            attrs = list(func.__annotations__.keys())
            if attrs:
                kwargs = {attrs[0]: attr_value}
                func_data = ThreadFuncData(func=func, kwargs=kwargs)
            else:
                func_data = ThreadFuncData(func=func, kwargs={})

        return func_data

    def _init_data_storage(self) -> DataStorage:
        ds_class = self._post_processing.data_storage
        return ds_class(model=self._post_processing.model)
