import asyncio
from threading import Thread
from typing import Optional

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
        func_data = self._build_func_data(instance=self._instance, method=self._method)
        asyncio.gather(*[func_data.func(**func_data.kwargs)])

    def execute(self, execute_data: InitPostProcessing) -> None:
        self._instance = execute_data.instance
        self._method = execute_data.method
        self._post_processing = execute_data.post_processing_data
        self.run()

    def _build_func_data(self, instance: T, method: Method) -> Optional[ThreadFuncData]:
        ds: DataStorage = self._init_data_storage()
        settings = self._post_processing.settings
        func_data: Optional[ThreadFuncData] = None
        if method in settings.methods:
            func = getattr(ds, settings.func_name)
            attr_value = getattr(instance, settings.instance_attr)
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
