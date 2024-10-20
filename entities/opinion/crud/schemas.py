from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class OpinionAttributes(TypedDict):
    text: str
    initiative_id: str


class OpinionRelations(TypedDict):
    creator: SchemaInstance


class OpinionRead(TypedDict):
    id: str
    attributes: OpinionAttributes
    relations: OpinionRelations


class OpinionCreate(TypedDict, total=False):
    id: str
    attributes: OpinionAttributes
    relations: OpinionRelations


class OpinionUpdate(OpinionCreate):
    pass
