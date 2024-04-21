from typing import TypedDict


class CommunityNameAttributes(TypedDict):
    name: str
    creator_id: str
    community_id: str


class CommunityNameRead(TypedDict):
    id: str
    attributes: CommunityNameAttributes


class CommunityNameCreate(TypedDict, total=False):
    id: str
    attributes: CommunityNameAttributes


class CommunityNameUpdate(CommunityNameCreate):
    pass
