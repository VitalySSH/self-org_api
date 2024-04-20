import abc
from typing import TypeVar

from fastapi import UploadFile
from pydantic import BaseModel

from datastorage.database.models import FileMetaData

T = TypeVar('T', bound=FileMetaData)


class FileStorage(abc.ABC):

    @abc.abstractmethod
    async def get_file_metadata(self, file_id: str) -> T:
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_file_path(file_metadata: FileMetaData) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_file(self, file: UploadFile, user_id: str) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_file(self, file_id: str, schema: BaseModel) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_file(self, file_id: str) -> None:
        raise NotImplementedError
