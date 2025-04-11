import logging
import traceback

from contextlib import asynccontextmanager
from typing import Generic, Type, Optional

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from datastorage.database.base import async_session_maker
from datastorage.interfaces import T

logger = logging.getLogger(__name__)


class DataStorage(Generic[T]):
    """DAL."""

    __abstract__ = True

    _model: Type[T]
    _session: Optional[AsyncSession]
    _background_tasks: Optional[BackgroundTasks]
    _is_external_session: bool

    def __init__(
            self,
            model: Type[T],
            session: Optional[AsyncSession] = None,
            background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        self._model = model
        self._session = session
        self._is_external_session = session is not None
        self._background_tasks = background_tasks

    @asynccontextmanager
    async def session_scope(self, read_only: bool = False):
        """Контекстный менеджер для управления сессией."""
        if self._is_external_session:
            yield
            return

        async with async_session_maker() as session:
            self._session = session
            try:
                async with session.begin():
                    yield
                if not read_only:
                    await session.commit()

            except Exception as original_e:
                await session.rollback()

                tb_str = traceback.format_exc()
                msg = (
                    f'Ошибка в session_scope (read_only={read_only}) в '
                    f'классе {self.__class__.__name__}:'
                )
                print(f'{msg}:\n{tb_str}')
                enriched_e = Exception(f'{msg} {str(original_e)}')
                enriched_e.__cause__ = original_e

                raise enriched_e from original_e

            finally:
                self._session = None
