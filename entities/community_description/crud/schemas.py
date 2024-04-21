from typing import TypedDict


class CommunityDescAttributes(TypedDict):
    value: str
    creator_id: str
    community_id: str


class CommunityDescRead(TypedDict):
    id: str
    attributes: CommunityDescAttributes


class CommunityDescCreate(TypedDict, total=False):
    id: str
    attributes: CommunityDescAttributes


class CommunityDescUpdate(CommunityDescCreate):
    pass
