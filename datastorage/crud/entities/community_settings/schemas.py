from typing import List, TypedDict

from datastorage.crud.entities.user.schemas import UserRead
from datastorage.crud.schemas.interfaces import SchemaInstance


class CSAttributes(TypedDict):
    name: str
    quorum: int
    vote: int


class CSRelations(TypedDict, total=False):
    user: SchemaInstance
    community: SchemaInstance
    init_categories: List[SchemaInstance]


class ReadComSettings(TypedDict, total=False):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class CreateComSettings(TypedDict, total=False):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class updateComSettings(CreateComSettings):
    pass
