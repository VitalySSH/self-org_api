from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class VIIAttributes(TypedDict):
    influence_type: str
    description: str


class VIIRelations(TypedDict, total=False):
    solution_version: SchemaInstance
    collective_interaction: SchemaInstance


class VIIRead(TypedDict):
    id: str
    attributes: VIIAttributes
    relations: VIIRelations


class VIICreate(TypedDict, total=False):
    id: str
    attributes: VIIAttributes
    relations: VIIRelations


class VIIUpdate(VIICreate):
    pass
