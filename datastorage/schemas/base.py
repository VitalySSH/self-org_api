from pydantic import BaseModel


class DirtyAttribute:
    """Тип поля схемы, который не подлежит изменению."""


dirty_attribute = DirtyAttribute()


class BaseUpdateScheme(BaseModel):
    class Config:
        arbitrary_types_allowed = True
