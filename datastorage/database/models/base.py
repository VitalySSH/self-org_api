from typing import Optional, List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datastorage.interfaces import SchemaInstance
from datastorage.utils import build_uuid

JOIN_DEPTH = 2


class Base(DeclarativeBase):
    EXCLUDE_READ_FIELDS: List[str] = []

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)

    def to_read_schema(
            self,
            model=None,
            recursion_level: Optional[int] = None,
    ) -> SchemaInstance:
        if recursion_level is None:
            recursion_level = 1
        if recursion_level > 10:
            raise Exception(f'Рекурсивная ошибка сериализации модели {self.__class__.__name__}')
        if model is None:
            model = self

        read_obj = {'id': model.id}
        attributes = {}
        relations = {}

        for field_name, value in model.__class__.__annotations__.items():
            if field_name in model.__class__.EXCLUDE_READ_FIELDS:
                continue

            field = getattr(model.__class__, field_name)
            class_attr = field.prop.class_attribute
            entity = getattr(field.prop, 'entity', None)
            if entity:
                direction = field.prop.direction.name
                if direction == 'MANYTOMANY':
                    m_2_m_result = []
                    for field_model in getattr(model, field_name):
                        if self.id == field_model.id:
                            raise Exception(f'Модель {self.__class__.__name__} '
                                            f'в связанных моделях ссылается сама на себя')
                        else:
                            field_model_obj = self.to_read_schema(
                                model=field_model, recursion_level=recursion_level + 1)
                            m_2_m_result.append(field_model_obj)

                    relations[field_name] = m_2_m_result

                elif direction == 'MANYTOONE':
                    field_model = getattr(model, field_name)
                    if str(self.id) == field_model.id:
                        raise Exception(f'Модель {self.__class__.__name__} '
                                        f'в связанных моделях ссылается сама на себя')
                    else:
                        relations[field_name] = self.to_read_schema(
                            model=field_model, recursion_level=recursion_level + 1)
            else:
                if len(class_attr.foreign_keys) == 0:
                    attributes[field_name] = getattr(model, field_name)

        read_obj['attributes'] = attributes
        read_obj['relations'] = relations

        return read_obj

