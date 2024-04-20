import asyncio
from threading import Thread
from typing import Optional

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import ThreadFuncData, PostProcessingData
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T


class CRUDPostProcessing(Thread, PostProcessing):
    """Постобработка запросов со стороны клиента."""

    _post_processing: PostProcessingData
    _instance: Optional[T]

    def run(self) -> None:
        func_data = self._build_func_data(self._instance)
        if func_data:
            asyncio.create_task(func_data.func(**func_data.kwargs))

    def execute(self, instance: T, post_processing_data: PostProcessingData) -> None:
        self._instance = instance
        self._post_processing = post_processing_data
        self.run()

    def _build_func_data(self, instance: T) -> Optional[ThreadFuncData]:
        ds: DataStorage = self._init_data_storage()
        func_data: Optional[ThreadFuncData] = None
        func = getattr(ds, self._post_processing.func_name)
        attr_value = getattr(instance, self._post_processing.instance_attr)
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
