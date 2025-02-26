from typing import TypedDict, Optional


class VotingOptionAttributes(TypedDict, total=False):
    content: str
    is_multi_select: bool
    creator_id: str
    initiative_id: Optional[str]
    rule_id: Optional[str]


class VotingOptionRead(TypedDict):
    id: str
    attributes: VotingOptionAttributes


class VotingOptionCreate(TypedDict, total=False):
    id: str
    attributes: VotingOptionAttributes


class VotingOptionUpdate(VotingOptionCreate):
    pass
