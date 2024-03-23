from typing import Optional, Union, List, TypedDict

from pydantic import BaseModel


from datastorage.crud.entities.initiative_category.schemas import ReadIC
from datastorage.crud.entities.user.schemas import ReadUser
from datastorage.crud.schemas.base import BaseUpdateScheme, DirtyAttribute, dirty_attribute
from datastorage.database.interfaces import SchemaInstance


class CSAttributes(TypedDict):
    name: str
    quorum: int
    vote: int


class CSRelations(TypedDict):
    user_rel: SchemaInstance
    community: SchemaInstance
    init_categories_rel: List[SchemaInstance]


class CreateComSet(TypedDict):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class BaseCS(BaseModel):
    name: str
    quorum: int
    vote: int


class ReadCS(BaseCS):
    id: str
    user: Optional[ReadUser]
    community: Optional[str]
    init_categories: List[ReadIC]

    class Config:
        from_attributes = True


class CreateCS(BaseCS):
    user: Optional[str] = None
    community: Optional[str] = None


class UpdateCS(BaseUpdateScheme):
    name: Union[str, DirtyAttribute] = dirty_attribute
    quorum: Union[int, DirtyAttribute] = dirty_attribute
    vote: Union[int, DirtyAttribute] = dirty_attribute
    user: Union[str, None, DirtyAttribute] = dirty_attribute
    community: Union[str, None, DirtyAttribute] = dirty_attribute
