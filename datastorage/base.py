from typing import Generic, Type, Optional

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from datastorage.interfaces import T


class DataStorage(Generic[T]):
    """DAL."""

    _model: Type[T]
    _session: Optional[AsyncSession]
    _background_tasks: Optional[BackgroundTasks]

    def __init__(
            self, model: Type[T],
            session: Optional[AsyncSession] = None,
            background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        self._model = model
        self._session = session
        self._background_tasks = background_tasks

    def set_session(self, session: AsyncSession) -> None:
        self._session = session

    async def close_session(self) -> None:
        if self._session:
            await self._session.close()

    async def invalidate_session(self) -> None:
        if self._session:
            await self._session.invalidate()
            self._session = None
