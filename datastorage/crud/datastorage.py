import json
from typing import Optional, Generic, Type, List, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Select

from datastorage.crud.exceptions import CRUDNotFound, CRUDConflict
from datastorage.crud.interfaces.base import DataStorage, T, S
from datastorage.crud.schemas.list import Filters, Operation, Orders, Direction, ListData
from datastorage.interfaces import SchemaInstance
from datastorage.utils import build_uuid


class CRUDDataStorage(Generic[T], DataStorage):
    """Выполняет CRUD-операция для модели."""

    _model: Type[T]
    _session: AsyncSession

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1

    def __init__(self, model: Type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def schema_to_model(self, schema: SchemaInstance, model: Type[T] = None) -> T:
        if model is None:
            model = self._model
        new_obj = model()

        return await self._update_object(obj=new_obj, schema=schema)

    async def _update_object(self, obj: T, schema: SchemaInstance, model: Type[T] = None) -> T:
        if model is None:
            model = self._model
        if not obj.id:
            obj.id = schema.get('id') or build_uuid()
        attributes = schema.get('attributes', {})
        for attr_name, attr_value in attributes.items():
            setattr(obj, attr_name, attributes.get(attr_name))

        relations = schema.get('relations', {})
        for rel_name, rel_value in relations.items():
            if isinstance(rel_value, list):
                many_to_many_objs: List[T] = []
                for sub_rel_value in rel_value:
                    rel_obj_id = sub_rel_value.get('id')
                    rel_obj_model = self._get_relation_model(model=model, field_name=rel_name)
                    rel_obj = await self.get(obj_id=rel_obj_id, model=rel_obj_model)
                    many_to_many_objs.append(rel_obj)
                setattr(obj, rel_name, many_to_many_objs)
            else:
                rel_obj_id = rel_value.get('id')
                rel_obj_model = self._get_relation_model(model=model, field_name=rel_name)
                rel_obj = await self.get(obj_id=rel_obj_id, model=rel_obj_model)
                setattr(obj, rel_name, rel_obj)

        return obj

    @staticmethod
    def _get_relation_model(model: Type[T], field_name: str) -> Type[S]:
        field = getattr(model, field_name, None)
        if field is None:
            raise Exception(f'Ошибка сериализации. '
                            f'Модель {model.__name__} не имеет аттрибута {field_name}')
        try:
            return field.prop.entity.class_
        except Exception as e:
            raise Exception(f'Аттрибут {field_name} модели '
                            f'{model.__name__} не является типом Relationship')

    async def get(self, obj_id: str, model: Type[T] = None) -> Optional[T]:
        if model is None:
            model = self._model
        return await self._session.get(entity=model, ident=obj_id)

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

    async def update(self, obj_id: str, schema: SchemaInstance) -> None:
        db_obj = await self.get(obj_id)
        if not db_obj:
            raise CRUDNotFound(f'Object with id {obj_id} not found')

        db_obj = await self._update_object(obj=db_obj, schema=schema)
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
        rows = await self._session.scalars(query)
        return list(rows.unique())

    async def first(self, list_data: ListData) -> Optional[T]:
        query = self._query_for_list(list_data)
        rows = await self._session.scalars(query)
        data = list(rows.unique())
        return data[0] if data else None

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
