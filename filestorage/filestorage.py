import errno
import logging
import os
import shutil
from datetime import datetime

import filetype as filetype
from fastapi import UploadFile
from sqlalchemy import select

from core.config import UPLOADED_FILES_PATH
from datastorage.base import DataStorage
from datastorage.database.models import FileMetaData
from datastorage.utils import build_uuid
from filestorage.interfaces import FileStorage, T

from filestorage.utils import create_file

logger = logging.getLogger(__name__)


class FileStorageApp(DataStorage[T], FileStorage):
    """Хранение и работа с файлами."""

    async def get_file_metadata(self, file_id: str) -> T:
        query = select(FileMetaData).where(FileMetaData.id == file_id)
        rows = await self._session.scalars(query)
        return rows.first()

    @staticmethod
    def get_file_path(file_metadata: FileMetaData) -> str:
        return os.path.abspath(
            os.path.join(UPLOADED_FILES_PATH, file_metadata.path, file_metadata.name))

    async def create_file(self, file: UploadFile, user_id: str) -> T:
        mimetype = filetype.guess(file.file).mime
        temp_file = create_file(
            file=file.file.read(), file_name=file.filename)
        full_path = os.path.abspath(
            os.path.join(UPLOADED_FILES_PATH, user_id, file.filename))
        self._get_directory(full_path)
        shutil.move(temp_file.name, full_path)

        file_metadata = FileMetaData(
            id=build_uuid(),
            name=file.filename,
            mimetype=mimetype,
            path=user_id
        )

        try:
            self._session.add(file_metadata)
            await self._session.commit()
            await self._session.refresh(file_metadata)
        except Exception as e:
            raise Exception(f'Файл не может быть сохранён: {e}')

        return file_metadata

    async def update_file(self, file_id: str, file: UploadFile) -> None:
        file_metadata = await self.get_file_metadata(file_id)
        if not file_metadata:
            raise Exception(f'Метаданные файла с id {file_id} не найдены')
        full_path = os.path.abspath(
            os.path.join(UPLOADED_FILES_PATH, file_metadata.path, file_metadata.name))
        self._delete_file_by_path(full_path)

        mimetype = filetype.guess(file.file).mime
        temp_file = create_file(
            file=file.file.read(), file_name=file.filename)
        full_path = os.path.abspath(
            os.path.join(UPLOADED_FILES_PATH, file_metadata.path, file.filename))
        self._get_directory(full_path)
        shutil.move(temp_file.name, full_path)

        file_metadata.name = file.filename
        file_metadata.mimetype = mimetype
        file_metadata.updated = datetime.now()

        try:
            await self._session.commit()
        except Exception as e:
            raise Exception(f'Ошибка обновления метаданных файла с id {file_id}: {e}')

    async def delete_file(self, file_id: str) -> None:
        file_metadata = await self.get_file_metadata(file_id)
        if not file_metadata:
            raise Exception(f'Метаданные файла с id {file_id} не найдены')
        full_path = os.path.abspath(
            os.path.join(UPLOADED_FILES_PATH, file_metadata.path, file_metadata.name))
        self._delete_file_by_path(full_path)

        try:
            await self._session.delete(file_metadata)
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise Exception(f'Метаданные файла с id {file_id} не могут быть удалены: {e}')

    @staticmethod
    def _delete_file_by_path(path: str) -> None:
        try:
            os.remove(path)
        except OSError as e:
            logger.exception(e)
            raise Exception('Файл не найден')

    @staticmethod
    def _get_directory(full_path: str):
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError(f'{directory} не существует.')
        return directory
