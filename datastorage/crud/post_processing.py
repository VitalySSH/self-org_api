import logging

from fastapi import BackgroundTasks
from typing import Optional, List

from datastorage.ao.datastorage import AODataStorage
from datastorage.crud.dataclasses import TaskFuncData, PostProcessingData
from datastorage.crud.interfaces.base import PostProcessing
from datastorage.interfaces import T

logger = logging.getLogger(__name__)


class CRUDPostProcessing(PostProcessing):
    """Постобработка запросов со стороны клиента."""

    post_processing_data: List[PostProcessingData]
    _instance: Optional[T]
    _instance_id: Optional[str]
    _background_tasks: BackgroundTasks

    def __init__(self, background_tasks: BackgroundTasks):
        self._background_tasks = background_tasks
        self._instance = None
        self._instance_id = None

    def execute(
            self, instance: Optional[T],
            post_processing_data: List[PostProcessingData],
            instance_id: Optional[str] = None,
    ) -> None:
        if self._background_tasks:
            self._instance = instance
            self._instance_id = instance_id
            self.post_processing_data = post_processing_data
            funcs_data = self._build_func_data_from_instance()
            self._background_tasks.add_task(self._execute_functions, *funcs_data)

    @staticmethod
    async def _execute_functions(*funcs_data):
        for func_data in funcs_data:
            try:
                await func_data.func(**func_data.kwargs)
            except Exception as e:
                logger.error(
                    f'POST_PROCESSING EXECUTE ERROR: {e.__str__()}'
                )

    def _build_func_data_from_instance(self) -> List[TaskFuncData]:
        funcs_data: List[TaskFuncData] = []
        for post_processing in self.post_processing_data:
            ds: AODataStorage = post_processing.data_storage()
            func = getattr(ds, post_processing.func_name)
            if self._instance:
                if post_processing.instance_attr:
                    attr_value = getattr(self._instance, post_processing.instance_attr)
                else:
                    attr_value = self._instance
            else:
                attr_value = self._instance_id
            if func and attr_value:
                attrs = list(func.__annotations__.keys())
                if attrs:
                    kwargs = {attrs[0]: attr_value}
                    funcs_data.append(TaskFuncData(func=func, kwargs=kwargs))
                else:
                    funcs_data.append(TaskFuncData(func=func, kwargs={}))

        return funcs_data
