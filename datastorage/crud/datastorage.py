import json
from typing import Optional, Generic, Type, Dict, List, cast, Any

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Select

from datastorage.crud.exceptions import CRUDNotFound, CRUDConflict
from datastorage.crud.interfaces.base import DataStorage, T, S
from datastorage.crud.schemas.list import Filters, Operation, Orders, Direction, ListData
from datastorage.crud.schemas.base import DirtyAttribute
from datastorage.utils import build_uuid


class CRUDDataStorage(Generic[T], DataStorage):
    """Выполняет CRUD-операция для модели."""

    _model: Type[T]
    _session: AsyncSession

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1
    __NOT_FOUND_ATTR = 'not_found_attr'

    def __init__(self, model: Type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    def schema_to_obj(self, schema: S) -> T:
        new_obj: Dict[str, Any] = {}
        for key in type(schema).model_fields.keys():
            value = getattr(schema, key, None)
            if type(value) == DirtyAttribute:
                continue

            new_obj[key] = value

        return self._model(**new_obj)

    @staticmethod
    def obj_to_schema(obj: T, schema: Type[S]) -> S:
        new_schema: Dict[str, Any] = {}
        for key in type(obj).__dict__.keys():
            if key[0] == '_':
                continue

            if schema.model_fields.get(key):
                new_schema[key] = getattr(obj, key, None)

        return schema(**new_schema)

    def obj_with_relations_to_schema(self, obj: T, schema: Type[S],
                                     recursion_level: Optional[int] = None) -> S:
        if recursion_level is None:
            recursion_level = 1
        if recursion_level > 10:
            raise Exception('Ошибка сериализации. '
                            'Схемы объектов циклически ссылаются друг на друга')
        new_schema: Dict[str, Any] = {}
        for key, value in self.__update_obj_data_with_relations(obj).items():
            if schema.model_fields.get(key):
                field_type = schema.model_fields.get(key).annotation
                try:
                    is_relation = issubclass(field_type, BaseModel)
                except TypeError:
                    args = field_type.__dict__.get('__args__') or []
                    is_relation = args and issubclass(args[0], BaseModel)
                    if is_relation:
                        field_type = args[0]
                if is_relation:
                    value = self.obj_with_relations_to_schema(
                        obj=value, schema=field_type, recursion_level=recursion_level + 1)

                new_schema[key] = value
        return schema(**new_schema)

    @staticmethod
    def __update_obj_data_with_relations(obj: T) -> dict:
        new_obj_data = {}
        for key in type(obj).__dict__.keys():
            if key[0] == '_':
                continue
            field_parts = key.rsplit('_', 1)
            if len(field_parts) > 1 and field_parts[-1] == 'rel':
                new_obj_data[field_parts[0]] = getattr(obj, key, None)
            else:
                if new_obj_data.get(key) is None:
                    new_obj_data[key] = getattr(obj, key, None)

        return new_obj_data

    async def get(self, obj_id: str) -> Optional[T]:
        return await self._session.get(entity=self._model, ident=obj_id)

    async def create(self, obj: T) -> T:
        if not obj.id:
            obj.id = build_uuid()
        try:
            self._session.add(obj)
            await self._session.commit()
            await self._session.refresh(obj)
        except IntegrityError as e:
            raise CRUDConflict(f'Объект модели {self._model.__name__} не может быть создан: {e}')
        return obj

    async def update(self, obj_id: str, schema: S) -> None:
        db_obj = await self.get(obj_id)
        if not db_obj:
            raise CRUDNotFound(f'Object with id {obj_id} not found')
        for key, value in schema.__dict__.items():
            if type(value) == DirtyAttribute:
                continue
            if self.__class__.__NOT_FOUND_ATTR != getattr(
                    db_obj, key, self.__class__.__NOT_FOUND_ATTR):
                setattr(db_obj, key, value)
        self._session.add(db_obj)
        await self._session.commit()
        await self._session.refresh(db_obj)

    async def delete(self, obj_id: str) -> None:
        db_obj = await self.get(obj_id)
        if not db_obj:
            raise CRUDNotFound(f'Object with id {obj_id} not found')
        try:
            await self._session.delete(db_obj)
            await self._session.commit()
            await self._session.refresh(db_obj)
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
        limit = list_data.pagination.limit if list_data.pagination else self.MAX_PAGE_SIZE
        skip = list_data.pagination.skip if list_data.pagination else self.DEFAULT_INDEX
        skip = (skip - 1) * limit
        filters = self._get_filter_params(list_data.filters)
        orders = self._get_order_params(list_data.orders)
        query = select(self._model).filter(*filters)
        query.order_by(*orders).limit(limit).offset(skip)

        return query
    
    def _get_filter_params(self, filters: Optional[Filters]) -> List:
        params = []
        for _filter in filters or []:
            field = getattr(self._model, _filter.field)
            operation = _filter.op
            value = _filter.val
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
            field = getattr(self._model, order.field, None)
            if field:
                if order.direction == Direction.DESC:
                    params.append(field.desc())
                else:
                    params.append(field.asc())

        return params
