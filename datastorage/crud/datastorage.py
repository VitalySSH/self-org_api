import json
from typing import Optional, Type, List, Any, cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, Select
from sqlalchemy.orm import selectinload, Load

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import PostProcessingData
from datastorage.crud.exceptions import CRUDNotFound, CRUDConflict, CRUDException
from datastorage.crud.interfaces.base import CRUD, Include
from datastorage.crud.interfaces.list import (
    Filters, Operation, Orders, Direction, ListData, Pagination
)
from datastorage.crud.interfaces.schema import SchemaInstance, S
from datastorage.crud.post_processing import CRUDPostProcessing
from datastorage.interfaces import T
from datastorage.utils import build_uuid


class CRUDDataStorage(DataStorage[T], CRUD):
    """Выполняет CRUD-операции для модели."""

    _post_processing_type = CRUDPostProcessing

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1

    async def schema_to_model(self, schema: S) -> T:
        """Сериализует схему в объект модели."""
        return await self._update_instance_from_schema(instance=self._model(), schema=schema)

    async def _update_instance_from_schema(self, instance: T, schema: SchemaInstance) -> T:
        model = type(instance)
        if not instance.id:
            instance.id = schema.get('id') or build_uuid()
        attributes = schema.get('attributes', {})
        for attr_name, attr_value in attributes.items():
            if getattr(type(instance), attr_name, False):
                setattr(instance, attr_name, attributes.get(attr_name))

        relations = schema.get('relations', {})
        for rel_name, rel_value in relations.items():
            if isinstance(rel_value, list):
                many_to_many_objs: List[T] = []
                for sub_rel_value in rel_value:
                    rel_obj_id = sub_rel_value.get('id')
                    if rel_obj_id:
                        rel_obj_model = self._get_relation_model(model=model, field_name=rel_name)
                        rel_obj = await self.get(instance_id=rel_obj_id, model=rel_obj_model)
                        many_to_many_objs.append(rel_obj)
                if many_to_many_objs:
                    setattr(instance, rel_name, many_to_many_objs)
            else:
                rel_obj_id = rel_value.get('id')
                if rel_obj_id:
                    rel_obj_model = self._get_relation_model(model=model, field_name=rel_name)
                    rel_obj = await self.get(instance_id=rel_obj_id, model=rel_obj_model)
                    setattr(instance, rel_name, rel_obj)

        return instance

    def execute_post_processing(
            self, instance: Optional[T],
            post_processing_data: List[PostProcessingData],
            instance_id: Optional[str] = None,
    ) -> None:
        post_processing = self._post_processing_type(self._background_tasks)
        post_processing.execute(
            instance=instance,
            post_processing_data=post_processing_data,
            instance_id=instance_id,
        )

    @staticmethod
    def get_relation_fields(schema: S) -> List[str]:
        return [key for key, value in schema.get('relations', {}).items() if value]

    @staticmethod
    def _get_relation_model(model: Type[T], field_name: str) -> Type[T]:
        field = getattr(model, field_name, None)
        if field is None:
            raise Exception(f'Ошибка сериализации. '
                            f'Модель {model.__name__} не имеет аттрибута {field_name}')
        try:
            return field.prop.entity.class_
        except Exception as e:
            raise Exception(f'Аттрибут {field_name} модели '
                            f'{model.__name__} не является типом Relationship: {e}')

    async def get(
            self, instance_id: str,
            include: Include = None,
            model: Type[T] = None
    ) -> Optional[T]:
        if model is None:
            model = self._model
        query = select(model).where(model.id == instance_id)
        if include:
            options = self._build_options(include)
            query = query.options(*options)
        try:
            rows = await self._session.scalars(query)
            return rows.first()
        except Exception as e:
            raise CRUDException(f'Не удалось получить объект с id {instance_id} '
                                f'модели {model.__name__}: {e}')

    def _build_options(self, include: List[str]) -> List[Load]:
        options = []
        for incl in include:
            option: Optional[Load] = None
            field_model: Type[T] = self._model
            current_field_name: Optional[str] = None
            for idx, field_name in enumerate(incl.split('.'), 1):
                if idx == 1:
                    current_field_name = field_name
                else:
                    field_ = getattr(field_model, current_field_name, None)
                    if field_:
                        field_model = field_.comparator.entity.class_
                        current_field_name = field_name
                    else:
                        raise CRUDException(f'Модель {field_model.__name__} не имеет атрибута'
                                            f' {field_name} указанный в include {incl}')

                field = getattr(field_model, field_name, None)
                if field:
                    if option:
                        option = option.selectinload(field)
                    else:
                        option = cast(Load, selectinload(field))
            if option:
                options.append(option)

        return options

    async def create(self, instance: T, relation_fields: Optional[List[str]] = None) -> T:
        if not instance.id:
            instance.id = build_uuid()
        relation_data = {rel_field: value for rel_field in relation_fields or []
                         if (value := getattr(instance, rel_field, None))}
        try:
            self._session.add(instance)
            await self._session.commit()
            await self._session.refresh(instance)
        except IntegrityError as e:
            raise CRUDConflict(f'Объект модели {self._model.__name__} не может быть создан: {e}')

        for field, value in relation_data.items():
            setattr(instance, field, value)

        return instance

    async def update(self, instance_id: str, schema: SchemaInstance) -> None:
        include = self.get_relation_fields(schema)
        instance = await self.get(instance_id=instance_id, include=include)
        if not instance:
            raise CRUDNotFound(
                f'Объект с id {instance_id} модели {self._model.__name__} не найден')

        try:
            await self._update_instance_from_schema(instance=instance, schema=schema)
            await self._session.commit()
        except Exception as e:
            raise CRUDConflict(
                f'Ошибка обновления объекта с id {instance_id} модели {self._model.__name__}: {e}')

    async def delete(self, instance_id: str) -> None:
        instance = await self.get(instance_id=instance_id)
        if not instance:
            raise CRUDNotFound(f'Объект с id {instance_id} не найден')
        try:
            await self._session.delete(instance)
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            raise CRUDConflict(f'Объект с id {instance_id} не может быть удалён: {e}')

    async def list(
            self, filters: Filters = None,
            orders: Orders = None,
            pagination: Pagination = None,
            include: Include = None,
    ) -> List[T]:
        list_data = ListData(filters=filters, orders=orders,
                             pagination=pagination, include=include)
        query = self._query_for_list(list_data)
        rows = await self._session.scalars(query)
        return list(rows)

    async def first(
            self, filters: Filters = None,
            orders: Orders = None,
            pagination: Pagination = None,
            include: Include = None,
    ) -> Optional[T]:
        list_data = ListData(filters=filters, orders=orders,
                             pagination=pagination, include=include)
        query = self._query_for_list(list_data)
        rows = await self._session.scalars(query)
        data = list(rows)
        return data[0] if data else None

    def _query_for_list(self, list_data: ListData) -> Select[Any]:
        limit = list_data.pagination.limit if list_data.pagination else self.MAX_PAGE_SIZE
        skip = list_data.pagination.skip if list_data.pagination else self.DEFAULT_INDEX
        skip = (skip - 1) * limit
        filters = self._get_filter_params(list_data.filters)
        orders = self._get_order_params(list_data.orders)
        query = select(self._model).filter(*filters)
        if list_data.include:
            options = self._build_options(list_data.include)
            query = query.options(*options)
        query.order_by(*orders).limit(limit).offset(skip)

        return query
    
    def _get_filter_params(self, filters: Filters) -> List:
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
                if isinstance(value, str):
                    value = json.loads(value)
                params.append(field.in_(value))
            elif operation == Operation.NOT_IN:
                if isinstance(value, str):
                    value = json.loads(value)
                params.append(field.notin_(value))
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

    def _get_order_params(self, orders: Orders = None) -> List:
        params = []
        for order in orders or []:
            field = getattr(self._model, order.field, None)
            if field:
                if order.direction == Direction.DESC:
                    params.append(field.desc())
                else:
                    params.append(field.asc())

        return params
