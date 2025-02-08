from typing import Optional, TypeVar

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datastorage.crud.interfaces.schema import SchemaInstance
from datastorage.utils import build_uuid

S = TypeVar('S')


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)

    def to_read_schema(self) -> S:
        """Вернёт сериализованный объект модели."""
        return self._to_read_schema()

    def _to_read_schema(
            self,
            instance: Optional[DeclarativeBase] = None,
            recursion_level: Optional[int] = None,
    ) -> SchemaInstance:
        if recursion_level is None:
            recursion_level = 1
        if recursion_level > 10:
            raise Exception(f'Рекурсивная ошибка сериализации модели {self.__class__.__name__}')
        if instance is None:
            instance = self

        read_obj = {'id': instance.id}
        attributes = {}
        relations = {}

        for field_name, value in instance.__class__.__annotations__.items():
            field = getattr(instance.__class__, field_name)
            class_attr = field.prop.class_attribute
            entity = getattr(field.prop, 'entity', None)
            if entity:
                direction = field.prop.direction.name
                if direction == 'MANYTOMANY':
                    m_2_m_result = []
                    for retrieved_instance in getattr(instance, field_name, []):
                        if self.id == retrieved_instance.id:
                            raise Exception(f'Модель {self.__class__.__name__} '
                                            f'в связанных моделях ссылается сама на себя')
                        else:
                            instance_schema = self._to_read_schema(
                                instance=retrieved_instance, recursion_level=recursion_level + 1)
                            m_2_m_result.append(instance_schema)

                    relations[field_name] = m_2_m_result

                elif direction == 'MANYTOONE':
                    retrieved_instance = getattr(instance, field_name)
                    if retrieved_instance:
                        if str(self.id) == retrieved_instance.id:
                            raise Exception(f'Модель {self.__class__.__name__} '
                                            f'в связанных моделях ссылается сама на себя')
                        else:
                            relations[field_name] = self._to_read_schema(
                                instance=retrieved_instance, recursion_level=recursion_level + 1)
                    else:
                        relations[field_name] = {}
            else:
                if len(class_attr.foreign_keys) == 0:
                    attributes[field_name] = getattr(instance, field_name)

        read_obj['attributes'] = attributes
        read_obj['relations'] = relations

        return read_obj
