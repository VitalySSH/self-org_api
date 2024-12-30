from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from datastorage.base import DataStorage
from datastorage.interfaces import T


class AODataStorage(DataStorage[T]):
    """Дополнительная бизнес-логика для модели."""

    def __init__(self, session: Optional[AsyncSession] = None):
        super().__init__(model=self.__class__._model, session=session)

