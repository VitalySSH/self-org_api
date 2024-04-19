from typing import TypedDict, Optional


class LikeAttributes(TypedDict):
    is_like: bool
    creator_id: str
    initiative_id: Optional[str]
    opinion_id: Optional[str]


class LikeRead(TypedDict):
    id: str
    attributes: LikeAttributes


class LikeCreate(TypedDict, total=False):
    id: str
    attributes: LikeAttributes


class LikeUpdate(LikeCreate):
    pass
