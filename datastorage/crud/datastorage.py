from typing import Optional, Generic,  Type, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datastorage.interfaces import DataStorage, T, S
from datastorage.utils import build_uuid


class CRUDDataStorage(Generic[T], DataStorage):
    """Выполняет CRUD-операция для модели."""

    _model: Type[T]
    _session: AsyncSession

    def __init__(self, model: Type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    def schema_to_obj(self, schema: S,
                      mapping: Optional[Dict[str, str]] = None) -> T:
        new_obj = {}
        for key in schema.__dict__.keys():
            value = getattr(schema, key, None)
            if mapping:
                new_key = mapping.get(key)
                key = new_key if new_key else key
            new_obj[key] = value
        return self._model(**new_obj)

    def obj_to_schema(self, schema: Type[S], obj: T,
                      mapping: Optional[Dict[str, str]] = None) -> S:
        new_schema = {}
        for key, value in obj.__dict__.items():
            if mapping:
                new_key = mapping.get(key)
                key = new_key if new_key else key
            new_schema[key] = value
        return schema(**new_schema)

    async def get(self, obj_id: str) -> Optional[T]:
        query = select(self._model).where(self._model.id == obj_id)
        rows = await self._session.execute(query)
        return rows.scalars().first()

    async def create(self, obj: T) -> T:
        if not obj.id:
            obj.id = build_uuid()
        async with self._session.begin():
            self._session.add(obj)
        await self._session.flush()
        return obj
