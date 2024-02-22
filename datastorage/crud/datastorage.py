import json
from typing import Optional, Generic, Type, Dict, List, cast, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Select

from datastorage.crud.dataclasses import ListData
from datastorage.crud.exceptions import CRUDNotFound, CRUDConflict
from datastorage.interfaces.base import DataStorage, T, S
from datastorage.interfaces.list import Filters, Operation, Orders, Direction
from datastorage.schemas.base import DirtyAttribute
from datastorage.utils import build_uuid


class CRUDDataStorage(Generic[T], DataStorage):
    """Выполняет CRUD-операция для модели."""

    _model: Type[T]
    _session: AsyncSession

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1

    def __init__(
            self,
            model: Type[T],
            session: AsyncSession,
    ) -> None:
        self._model = model
        self._session = session

    def schema_to_obj(self, schema: S,
                      mapping: Optional[Dict[str, str]] = None) -> T:
        new_obj: Dict[str, Any] = {}
        for key in schema.__dict__.keys():
            value = getattr(schema, key, None)
            if mapping:
                new_key = mapping.get(key)
                key = new_key if new_key else key
            new_obj[key] = value
        return self._model(**new_obj)

    def obj_to_schema(self, obj: T, schema: Type[S],
                      mapping: Optional[Dict[str, str]] = None) -> S:
        new_schema: Dict[str, Any] = {}
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
        self._session.add(obj)
        await self._session.commit()
        return obj

    async def update(self, obj_id: str, schema: S) -> None:
        db_obj = await self.get(obj_id)
        if not db_obj:
            raise CRUDNotFound(f'Object with id {obj_id} not found')
        for key, value in schema.__dict__.items():
            if type(value) == DirtyAttribute:
                continue
            if getattr(db_obj, key, False):
                setattr(db_obj, key, value)
        self._session.add(db_obj)
        await self._session.commit()

    async def delete(self, obj_id: str) -> None:
        db_obj = await self.get(obj_id)
        if not db_obj:
            raise CRUDNotFound(f'Object with id {obj_id} not found')
        try:
            await self._session.delete(db_obj)
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise CRUDConflict(f"Object with id {obj_id} can't be deleted: {e}")

    async def list(self, list_data: ListData) -> List[T]:
        query = self._query_for_list(list_data)
        rows = await self._session.execute(query)
        return cast(List[T], rows.scalars().all())

    async def first(self, list_data: ListData) -> T:
        query = self._query_for_list(list_data)
        rows = await self._session.execute(query)
        return rows.scalars().first()

    def _query_for_list(self, list_data: ListData) -> Select[Any]:
        limit = (list_data.pagination or {}).get('limit') or self.MAX_PAGE_SIZE
        skip = (list_data.pagination or {}).get('skip') or self.DEFAULT_INDEX
        skip = (skip - 1) * limit
        filters = self._get_filter_params(list_data.filters)
        orders = self._get_order_params(list_data.orders)
        query = select(self._model).filter(*filters)
        query.order_by(*orders).limit(limit).offset(skip)

        return query
    
    def _get_filter_params(self, filters: Optional[Filters]) -> List:
        params = []
        for _filter in filters or []:
            field = getattr(self._model, _filter.get('field'))
            operation = _filter.get('op')
            value = _filter.get('val')
            if operation == Operation.EQ:
                params.append(field == value)
            elif operation == Operation.NOT_EQ:
                params.append(field != value)
            elif operation == Operation.IN:
                params.append(field.in_(json.loads(value)))
            elif operation == Operation.NOT_IN:
                params.append(field.notin_(json.loads(value)))
            elif operation == Operation.LIKE:
                params.append(field.like(f'%{value}%'))
            elif operation == Operation.ILIKE:
                params.append(field.ilike(f'%{value}%'))
            elif operation == Operation.GT:
                params.append(field > value)
            elif operation == Operation.GTE:
                params.append(field >= value)
            elif operation == Operation.LT:
                params.append(field < value)
            elif operation == Operation.LTE:
                params.append(field <= value)
            elif operation == Operation.IEQ:
                params.append(func.lower(field) == func.lower(value))
            elif operation == Operation.NULL:
                params.append(field.is_(None) if value else field.isnot(None))
            elif operation == Operation.BETWEEN:
                params.append(field.between(*json.loads(value)))

        return params

    def _get_order_params(self, orders: Optional[Orders] = None) -> List:
        params = []
        for order in orders or []:
            field_name = order.get('field')
            direction = order.get('direction')
            field = getattr(self._model, field_name, None)
            if field:
                if direction == Direction.DESC:
                    params.append(field.desc())
                else:
                    params.append(field.asc())

        return params
