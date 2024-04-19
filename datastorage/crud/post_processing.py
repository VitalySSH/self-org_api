import asyncio
from threading import Thread
from typing import Optional, List

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import (
    ThreadFuncData, PostProcessingData, InitPostProcessing
)
from datastorage.crud.enum import Method
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T


class CRUDPostProcessing(Thread, PostProcessing):
    """Постобработка запросов со стороны клиента."""

    _post_processing: PostProcessingData
    _instance: Optional[T]
    _method: Optional[Method]

    def run(self) -> None:
        funcs_data = self._build_thread_func_data(
            instance=self._instance, method=self._method)
        if self._post_processing.is_consistently:
            for func_data in funcs_data:
                asyncio.run(self._wrap_consistently_task(func_data))
        else:
            tasks = [func_data.func(**func_data.kwargs) for func_data in funcs_data]
            asyncio.gather(*tasks)

    def execute(self, execute_data: InitPostProcessing) -> None:
        self._instance = execute_data.instance
        self._method = execute_data.method
        self._post_processing = execute_data.post_processing_data
        self.run()

    @staticmethod
    async def _wrap_consistently_task(data: ThreadFuncData):
        await data.func(**data.kwargs)

    def _build_thread_func_data(self, instance: T, method: Method) -> List[ThreadFuncData]:
        ds: DataStorage = self._init_data_storage()
        funcs_data: List[ThreadFuncData] = []
        for settings in self._post_processing.settings:
            if method not in settings.methods:
                continue
            func = getattr(ds, settings.func_name)
            attr_value = getattr(instance, settings.instance_attr)
            if func and attr_value:
                attrs = list(func.__annotations__.keys())
                if attrs:
                    kwargs = {attrs[0]: attr_value}
                    func_data = ThreadFuncData(func=func, kwargs=kwargs)
                else:
                    func_data = ThreadFuncData(func=func, kwargs={})

                funcs_data.append(func_data)

        return funcs_data

    def _init_data_storage(self) -> DataStorage:
        ds_class = self._post_processing.data_storage
        return ds_class(model=self._post_processing.model)
