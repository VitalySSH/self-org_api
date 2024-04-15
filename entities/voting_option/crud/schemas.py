from typing import TypedDict, Optional


class VotingOptionAttributes(TypedDict):
    content: str
    creator_id: str
    initiative_id: Optional[str]


class VotingOptionRead(TypedDict):
    id: str
    attributes: VotingOptionAttributes


class VotingOptionCreate(TypedDict, total=False):
    id: str
    attributes: VotingOptionAttributes


class VotingOptionUpdate(VotingOptionCreate):
    pass
