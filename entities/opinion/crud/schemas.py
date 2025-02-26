from datetime import datetime
from typing import TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class OpinionAttributes(TypedDict, total=False):
    text: str
    initiative_id: Optional[str]
    rule_id: Optional[str]
    created: datetime


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
