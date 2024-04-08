from typing import TypedDict, Optional

from datastorage.crud.schemas.interfaces import SchemaInstance


class OpinionAttributes(TypedDict):
    text: str
    likes_count: Optional[int]
    dislikes_count: Optional[int]
    current_user_like: Optional[bool]


class OpinionRelations(TypedDict):
    creator: SchemaInstance
    initiative: SchemaInstance


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
