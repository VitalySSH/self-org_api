from typing import TypedDict

from datastorage.crud.schemas.interfaces import SchemaInstance


class InitCategoryAttributes(TypedDict):
    name: str


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
