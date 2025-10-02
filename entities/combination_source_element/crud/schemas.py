from datetime import datetime
from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class CSEAttributes(TypedDict):
    element_description: str
    element_context: str


class CSERelations(TypedDict, total=False):
    source_solution: SchemaInstance
    combination: SchemaInstance


class CSERead(TypedDict):
    id: str
    attributes: CSEAttributes
    relations: CSERelations


class CSECreate(TypedDict, total=False):
    id: str
    attributes: CSEAttributes
    relations: CSERelations


class CSEUpdate(CSECreate):
    pass
