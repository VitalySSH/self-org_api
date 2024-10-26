from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class CategoryAttributes(TypedDict):
    name: str
    community_id: str
    creator_id: str


class CategoryRelations(TypedDict, total=False):
    status: SchemaInstance


class CategoryRead(TypedDict):
    id: str
    attributes: CategoryAttributes
    relations: CategoryRelations


class CategoryCreate(TypedDict, total=False):
    id: str
    attributes: CategoryAttributes
    relations: CategoryRelations


class CategoryUpdate(CategoryCreate):
    pass
