from datetime import datetime
from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class SVAttributes(TypedDict, total=False):
    content: str
    change_description: str
    version_number: int
    created_at: datetime


class SVRelations(TypedDict, total=False):
    solution: SchemaInstance
    influences: List[SchemaInstance]


class SVRead(TypedDict):
    id: str
    attributes: SVAttributes
    relations: SVRelations


class SVCreate(TypedDict, total=False):
    id: str
    attributes: SVAttributes
    relations: SVRelations


class SVUpdate(SVCreate):
    pass
