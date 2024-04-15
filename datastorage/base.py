from typing import Generic, Type

from sqlalchemy.ext.asyncio import AsyncSession

from datastorage.interfaces import T


class DataStorage(Generic[T]):
    """DAL."""

    _model: Type[T]
    _session: AsyncSession

    def __init__(self, model: Type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session
