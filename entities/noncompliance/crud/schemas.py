from typing import TypedDict


class NoncomplianceAttributes(TypedDict):
    name: str
    community_id: str
    creator_id: str


class NoncomplianceRead(TypedDict):
    id: str
    attributes: NoncomplianceAttributes


class NoncomplianceCreate(TypedDict, total=False):
    id: str
    attributes: NoncomplianceAttributes


class NoncomplianceUpdate(NoncomplianceCreate):
    pass
