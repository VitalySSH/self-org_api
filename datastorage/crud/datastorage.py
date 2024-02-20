import json
from typing import Optional, Generic, Type, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from datastorage.crud.dataclasses import ListData
from datastorage.interfaces.base import DataStorage, T, S, RS
from datastorage.interfaces.list import Filters, Operation, Orders, Direction
from datastorage.utils import build_uuid


class CRUDDataStorage(Generic[T], DataStorage):
    """Выполняет CRUD-операция для модели."""

    _model: Type[T]
    _read_schema: Type[RS]
    _session: AsyncSession

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1

    def __init__(
            self,
            model: Type[T],
            read_schema: Type[RS],
            session: AsyncSession,
    ) -> None:
        self._model = model
        self._read_schema = read_schema
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

    def obj_to_schema(self, obj: T,
                      mapping: Optional[Dict[str, str]] = None) -> RS:
        new_schema = {}
        for key, value in obj.__dict__.items():
            if mapping:
                new_key = mapping.get(key)
                key = new_key if new_key else key
            new_schema[key] = value
        return self._read_schema(**new_schema)

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

    async def list(self, list_data: ListData) -> List[T]:
        limit = (list_data.pagination or {}).get('limit') or self.MAX_PAGE_SIZE
        skip = (list_data.pagination or {}).get('skip') or self.DEFAULT_INDEX
        skip = (skip - 1) * limit
        filters = self._get_filter_params(list_data.filters)
        orders = self._get_order_params(list_data.orders)
        query = select(self._model).filter(*filters)
        query.order_by(*orders).limit(limit).offset(skip)
        rows = await self._session.execute(query)
        return [self.obj_to_schema(row[0]) for row in rows.fetchall()]
    
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
