from typing import TypedDict


class CommunityNameAttributes(TypedDict, total=False):
    name: str
    creator_id: str
    community_id: str
    is_readonly: bool


class CommunityNameRead(TypedDict):
    id: str
    attributes: CommunityNameAttributes


class CommunityNameCreate(TypedDict, total=False):
    id: str
    attributes: CommunityNameAttributes


class CommunityNameUpdate(CommunityNameCreate):
    pass
