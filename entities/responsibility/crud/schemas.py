from typing import TypedDict


class ResponsibilityAttributes(TypedDict):
    name: str
    community_id: str
    creator_id: str


class ResponsibilityRead(TypedDict):
    id: str
    attributes: ResponsibilityAttributes


class ResponsibilityCreate(TypedDict, total=False):
    id: str
    attributes: ResponsibilityAttributes


class ResponsibilityUpdate(ResponsibilityCreate):
    pass
