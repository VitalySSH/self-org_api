from typing import TypedDict, Optional

from datastorage.crud.interfaces.base import SchemaInstance


class OpinionAttributes(TypedDict):
    text: str
    initiative_id: str


class OpinionReadOnly(TypedDict):
    likes_count: Optional[int]
    dislikes_count: Optional[int]
    current_user_like: Optional[bool]


class OpinionRelations(TypedDict):
    creator: SchemaInstance


class OpinionRead(TypedDict):
    id: str
    attributes: OpinionAttributes
    readonly: OpinionReadOnly
    relations: OpinionRelations


class OpinionCreate(TypedDict, total=False):
    id: str
    attributes: OpinionAttributes
    relations: OpinionRelations


class OpinionUpdate(OpinionCreate):
    pass
