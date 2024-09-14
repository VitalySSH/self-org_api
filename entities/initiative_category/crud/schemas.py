from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class InitCategoryAttributes(TypedDict):
    name: str
    community_id: str


class InitCategoryRelations(TypedDict):
    creator: SchemaInstance
    status: SchemaInstance


class InitCategoryRead(TypedDict):
    id: str
    attributes: InitCategoryAttributes
    relations: InitCategoryRelations


class InitCategoryCreate(TypedDict, total=False):
    id: str
    attributes: InitCategoryAttributes
    relations: InitCategoryRelations


class InitCategoryUpdate(InitCategoryCreate):
    pass
