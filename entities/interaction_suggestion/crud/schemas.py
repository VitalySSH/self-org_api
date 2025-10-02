from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class ISAttributes(TypedDict):
    element_description: str
    integration_advice: str
    source_solutions_count: int
    reasoning: str


class ISRelations(TypedDict, total=False):
    interaction: SchemaInstance


class ISRead(TypedDict):
    id: str
    attributes: ISAttributes
    relations: ISRelations


class ISCreate(TypedDict, total=False):
    id: str
    attributes: ISAttributes
    relations: ISRelations


class ISUpdate(ISCreate):
    pass
