from typing import Optional, TypeVar, Dict, Any

from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy import inspect as sqlalchemy_inspect

from datastorage.crud.interfaces.schema import (
    SchemaInstance, Relations, RelationsSchema
)

S = TypeVar('S')


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = ...

    def to_read_schema(self) -> S:
        """Вернёт сериализованный объект модели."""
        return self._to_read_schema()

    def _to_read_schema(
            self,
            instance: Optional[DeclarativeBase] = None,
            recursion_level: Optional[int] = None,
            processing_objects: Optional[set] = None,
    ) -> SchemaInstance:
        if recursion_level is None:
            recursion_level = 1
        if processing_objects is None:
            processing_objects = set()

        if recursion_level > 10:
            raise Exception(f'Рекурсивная ошибка сериализации '
                            f'модели {self.__class__.__name__}')
        if instance is None:
            instance = self

        # Создаем уникальный ключ для объекта
        obj_key = (type(instance).__name__, instance.id)

        if obj_key in processing_objects:
            return {
                'id': instance.id,
                'attributes': {},
                'relations': {}
            }

        processing_objects.add(obj_key)

        read_obj: SchemaInstance = {'id': instance.id}
        attributes: Dict[str, Any] = {}
        relations: Relations = {}

        for field_name, value in instance.__class__.__annotations__.items():
            field = getattr(instance.__class__, field_name)
            class_attr = field.prop.class_attribute
            entity = getattr(field.prop, 'entity', None)
            if entity:
                direction = field.prop.direction.name
                if direction in ['MANYTOMANY', 'ONETOMANY']:
                    m_2_m_result = []
                    collection = getattr(instance, field_name, [])

                    for retrieved_instance in collection:
                        state = sqlalchemy_inspect(retrieved_instance)

                        # Пропускаем несохраненные объекты
                        if state.pending:
                            continue

                        related_obj_key = (type(retrieved_instance).__name__,
                                           retrieved_instance.id)
                        if related_obj_key not in processing_objects:
                            instance_schema = self._to_read_schema(
                                instance=retrieved_instance,
                                recursion_level=recursion_level + 1,
                                processing_objects=processing_objects.copy()
                            )
                            m_2_m_result.append(instance_schema)

                    relations[field_name] = m_2_m_result

                elif direction == 'MANYTOONE':
                    retrieved_instance = getattr(instance, field_name)
                    if retrieved_instance:
                        related_obj_key = (type(retrieved_instance).__name__,
                                           retrieved_instance.id)
                        if related_obj_key not in processing_objects:
                            relations[field_name] = self._to_read_schema(
                                instance=retrieved_instance,
                                recursion_level=recursion_level + 1,
                                processing_objects=processing_objects.copy()
                            )
                        else:
                            relations[field_name] = RelationsSchema(
                                id=retrieved_instance.id,
                                attributes={},
                                relations={},
                            )
                    else:
                        relations[field_name] = {}
            else:
                if len(class_attr.foreign_keys) == 0:
                    attr_value = getattr(instance, field_name)
                    # TODO: сделать обработку поля типа JSON,
                    #  конвертировать в строку
                    attributes[field_name] = attr_value

        read_obj['attributes'] = attributes
        read_obj['relations'] = relations

        processing_objects.discard(obj_key)

        return read_obj
