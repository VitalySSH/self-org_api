from typing import TypedDict


class OpinionAttributes(TypedDict):
    text: str
    creator_id: str


class OpinionRead(TypedDict):
    id: str
    attributes: OpinionAttributes


class OpinionCreate(TypedDict, total=False):
    id: str
    attributes: OpinionAttributes


class OpinionUpdate(OpinionCreate):
    pass
