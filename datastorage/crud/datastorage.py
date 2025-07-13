import json
from datetime import datetime, date
from typing import Optional, Type, List, Any, cast, Dict, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, inspect, JSON
from sqlalchemy.orm import selectinload, Load, RelationshipProperty

from datastorage.base import DataStorage
from datastorage.crud.dataclasses import ListResponse
from datastorage.crud.exceptions import (
    CRUDNotFound, CRUDConflict, CRUDException, CRUDOperationError
)
from datastorage.crud.interfaces.base import CRUD, Include
from datastorage.crud.interfaces.list import (
    Filters, Operation, Orders, Direction, Pagination, PaginationModel
)
from datastorage.crud.interfaces.schema import SchemaInstance, S, Relations
from datastorage.crud.post_processing import CRUDPostProcessing
from datastorage.interfaces import T
from datastorage.crud.dataclasses import PostProcessingData
from entities.user_community_settings.model import UserCommunitySettings


class CRUDDataStorage(DataStorage[T], CRUD):
    """Выполняет CRUD-операции для модели."""

    _post_processing_type = CRUDPostProcessing

    MAX_PAGE_SIZE = 20
    DEFAULT_INDEX = 1
    MAX_INCLUDE_DEPTH = 5

    async def schema_to_model(self, schema: S) -> T:
        """Сериализует схему в объект модели."""
        return await self._update_instance_from_schema(
            instance=self._model(), schema=schema
        )

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
        return [key for key, value in schema.get('relations', {}).items()]

    async def get(
            self, instance_id: str,
            include: Include = None,
            model: Type[T] = None,
    ) -> Union[None, T, Any]:
        if model is None:
            model = self._model
        query = select(model).where(model.id == instance_id)
        if include:
            options = self._build_options(include=include, model=model)
            query = query.options(*options)
        try:
            return await self._session.scalar(query)
        except Exception as e:
            raise CRUDException(
                f'Не удалось получить объект с id {instance_id} '
                f'модели {model.__name__}: {e.__str__()}'
            )

    async def create(
            self, instance: T,
            include: Include = None
    ) -> T:
        relation_data = {
            rel_field: value for rel_field in include or []
            if (value := getattr(instance, rel_field, None))
        }
        try:
            self._session.add(instance)
            await self._session.flush([instance])
            await self._session.refresh(instance)
        except IntegrityError as e:
            raise CRUDConflict(f'Объект модели {self._model.__name__} '
                               f'не может быть создан: {e.__str__()}')

        for field, value in relation_data.items():
            setattr(instance, field, value)

        return instance

    async def update(self, instance_id: str, schema: SchemaInstance) -> None:
        include = self.get_relation_fields(schema)
        instance = await self.get(instance_id=instance_id, include=include)
        if not instance:
            raise CRUDNotFound(f'Объект с id {instance_id} модели '
                               f'{self._model.__name__} не найден')

        try:
            await self._update_instance_from_schema(
                instance=instance,
                schema=schema
            )
            await self._session.flush([instance])
        except Exception as e:
            raise CRUDConflict(
                f'Ошибка обновления объекта с id {instance_id} '
                f'модели {self._model.__name__}: {e.__str__()}'
            )

    async def delete(self, instance_id: str) -> None:
        instance = await self.get(instance_id=instance_id)
        if not instance:
            raise CRUDNotFound(f'Объект с id {instance_id} не найден')
        try:
            await self._session.delete(instance)
        except Exception as e:
            raise CRUDConflict(
                f'Объект с id {instance_id} не '
                f'может быть удалён: {e.__str__()}'
            )

    async def list(
            self,
            filters: Optional[Filters] = None,
            orders: Optional[Orders] = None,
            pagination: Optional[Pagination] = None,
            include: Optional[Include] = None,
            model: Type[T] = None,
    ) -> ListResponse[Union[T, Any]]:
        if model is None:
            model = self._model

        filters = self._get_filter_params(filters=filters, model=model)
        base_query = select(model).filter(*filters)

        try:
            total_query = (
                select(func.count())
                .select_from(base_query.subquery())
            )
            total = await self._session.scalar(total_query)
        except Exception as e:
            raise CRUDOperationError(
                f'Ошибка фильтрации при получения списка объектов '
                f'модели {self._model.__name__}: {e.__str__()}'
            )

        orders = self._get_order_params(orders)
        limit = pagination.limit if pagination else self.MAX_PAGE_SIZE
        skip = pagination.skip if pagination else self.DEFAULT_INDEX
        skip = (skip - 1) * limit

        if include:
            options = self._build_options(include=include, model=model)
            base_query = base_query.options(*options)

        base_query = base_query.order_by(*orders).offset(skip).limit(limit)
        rows = await self._session.scalars(base_query)

        return ListResponse(data=list(rows), total=total)

    async def first(
            self,
            filters: Optional[Filters] = None,
            orders: Optional[Orders] = None,
            include: Optional[Include] = None,
            model: Type[T] = None,
    ) -> Optional[T]:
        resp = await self.list(
            filters=filters,
            orders=orders,
            pagination=PaginationModel(skip=1, limit=1),
            include=include,
            model=model,
        )

        return resp.data[0] if resp.total > 0 else None

    async def get_user_ids_from_community(
            self,
            community_id: str,
            is_delegates: bool,
            current_user_id: str,
    ) -> List[str]:
        """Получить список id пользователей в сообществе."""
        # FIXME: вынести этот метод в другое место
        query_filters = [
            UserCommunitySettings.community_id == community_id,
            UserCommunitySettings.is_blocked.is_not(True),
        ]
        if is_delegates:
            query_filters += [
                UserCommunitySettings.is_not_delegate.is_not(True),
                UserCommunitySettings.user_id != current_user_id,
            ]
        query = (
            select(UserCommunitySettings.user_id)
            .where(*query_filters)
        )
        user_cs_data = await self._session.execute(query)

        return [it[0] for it in user_cs_data.all()]

    async def _update_instance_from_schema(
            self, instance: T, schema: SchemaInstance
    ) -> T:
        self._update_attributes(instance, schema.get('attributes', {}))
        await self._update_relations(instance, schema.get('relations', {}))

        return instance

    def _update_attributes(
            self, instance: T,
            attributes: Dict[str, Any]
    ) -> None:
        for attr_name, attr_value in attributes.items():
            if hasattr(instance, attr_name):
                if (self._is_json_field(instance, attr_name) and
                        isinstance(attr_value, str)):
                    try:
                        attr_value = json.loads(attr_value)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            f"Поле {attr_name} должно "
                            f"быть валидным JSON: {e.__str__()}"
                        )

                setattr(instance, attr_name, attr_value)

    async def _update_relations(
            self, instance: T,
            relations: Relations
    ) -> None:
        model = type(instance)
        for rel_name, rel_value in relations.items():
            if isinstance(rel_value, list):
                many_to_many_objs = await self._fetch_many_to_many(
                    rel_values=rel_value, model=model, rel_name=rel_name
                )
                setattr(instance, rel_name, many_to_many_objs)
            elif isinstance(rel_value, dict):
                related_obj = await self._fetch_relation(
                    rel_value=rel_value, model=model, rel_name=rel_name
                )
                setattr(instance, rel_name, related_obj)

    async def _fetch_many_to_many(
            self, rel_values: List[SchemaInstance],
            model: Type[T],
            rel_name: str
    ) -> List[T]:
        objs = []
        for rel_value in rel_values:
            rel_obj = await self._fetch_relation(rel_value, model, rel_name)
            if rel_obj:
                objs.append(rel_obj)

        return objs

    async def _fetch_relation(
            self, rel_value: SchemaInstance,
            model: Type[T],
            rel_name: str
    ) -> Optional[T]:
        rel_obj_id = rel_value.get('id')
        if not rel_obj_id:
            return None

        rel_obj_model = self._get_relation_model(
            model=model, field_name=rel_name
        )

        return await self.get(instance_id=rel_obj_id, model=rel_obj_model)

    @staticmethod
    def _get_relation_model(model: Type[T], field_name: str) -> Type[T]:
        field = getattr(model, field_name, None)
        if field is None:
            raise Exception(
                f'Ошибка сериализации. Модель {model.__name__} '
                f'не имеет аттрибута {field_name}'
            )
        try:
            return field.prop.entity.class_
        except Exception as e:
            raise Exception(
                f'Аттрибут {field_name} модели {model.__name__}'
                f' не является типом Relationship: {e.__str__()}'
            )

    @staticmethod
    def _is_json_field(instance: T, field: str) -> bool:
        """Проверяет, является ли поле модели JSON-полем."""
        field_type = inspect(instance.__class__).columns[field].type

        return isinstance(field_type, JSON)

    def _build_options(self, include: List[str], model: Type[T]) -> List[Load]:
        """Создаёт опции для загрузки связанных сущностей."""
        options = []
        for incl in include:
            option: Optional[Load] = None
            field_model: Type[T] = model
            current_field_name: Optional[str] = None
            fields: List[str] = incl.split('.')

            if len(fields) > self.__class__.MAX_INCLUDE_DEPTH:
                raise CRUDException(
                    f'Глубина вложенности для include "{incl}" '
                    f'превышает {self.__class__.MAX_INCLUDE_DEPTH}'
                )

            for idx, field_name in enumerate(fields, 1):
                if idx == 1:
                    current_field_name = field_name
                else:
                    field_ = getattr(field_model, current_field_name, None)
                    if field_:
                        field_model = field_.comparator.entity.class_
                        current_field_name = field_name
                    else:
                        raise CRUDException(
                            f'Модель {field_model.__name__} не имеет атрибута '
                            f'{field_name} указанный в include {incl}'
                        )

                field = getattr(field_model, field_name, None)
                if field:
                    if option:
                        option = option.selectinload(field)
                    else:
                        option = cast(Load, selectinload(field))
            if option:
                options.append(option)

        return options

    def _get_filter_params(
            self, filters: Filters,
            model: Type[T]
    ) -> List:
        """Формирует список параметров для фильтрации."""
        params = []
        for _filter in filters or []:

            try:
                parts = _filter.field.split('.')
                condition = self._build_condition(
                    model=model,
                    parts=parts,
                    operation=_filter.op,
                    value=_filter.val,
                )
                params.append(condition)
            except AttributeError as e:
                raise CRUDException(
                    f'Неверное поле фильтра '
                    f'{_filter.field}: {e.__str__()}'
                )

        return params

    def _build_condition(
            self, model: Type[T],
            parts: List[str],
            operation: Operation,
            value: Any,
    ) -> Any:
        if len(parts) == 1:
            field_name = parts[0]
            field = getattr(model, field_name)
            # FIXME: переделать
            field_types = (
                model.__annotations__.
                get(field_name).__dict__.get('__args__')
            )
            is_date = (
                    field_types and (
                    field_types[0] == date or field_types[0] == datetime
                )
            )

            return self._apply_operation(field, operation, value, is_date)
        else:

            current_part = parts[0]
            remaining_parts = parts[1:]
            rel = getattr(model, current_part)
            rel_prop = rel.property
            if not isinstance(rel_prop, RelationshipProperty):
                raise AttributeError(
                    f'Поле {current_part} не является relation'
                )
            rel_model = rel_prop.entity.class_
            sub_condition = self._build_condition(
                model=rel_model,
                parts=remaining_parts,
                operation=operation,
                value=value
            )
            if rel_prop.uselist:

                return rel.any(sub_condition)
            else:

                return rel.has(sub_condition)

    @staticmethod
    def _apply_operation(
            field: Any,
            operation: Operation,
            value: Any,
            is_date: bool = False,
    ) -> Any:
        if is_date:
            try:
                value = list(map(
                    lambda it: datetime.fromisoformat(it),
                    json.loads(value),
                ))
            except json.JSONDecodeError:
                value = datetime.fromisoformat(value)

        if operation == Operation.EQ:
            return field == value
        elif operation == Operation.NOT_EQ:
            return field != value
        elif operation == Operation.IN:
            if isinstance(value, str):
                value = json.loads(value)
            return field.in_(value)
        elif operation == Operation.NOT_IN:
            if isinstance(value, str):
                value = json.loads(value)
            return field.notin_(value)
        elif operation == Operation.LIKE:
            return field.like(f'%{value}%')
        elif operation == Operation.ILIKE:
            return field.ilike(f'%{value}%')
        elif operation == Operation.GT:
            return field > value
        elif operation == Operation.GTE:
            return field >= value
        elif operation == Operation.LT:
            return field < value
        elif operation == Operation.LTE:
            return field <= value
        elif operation == Operation.IEQ:
            return func.lower(field) == func.lower(value)
        elif operation == Operation.NULL:
            return field.is_(None) if value else field.isnot(None)
        elif operation == Operation.BETWEEN:
            return field.between(*value)
        else:
            raise CRUDException(f'Неподдерживаемая операция {operation}')

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
