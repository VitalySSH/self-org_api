from typing import TypedDict, Optional


class RecountingVote(TypedDict, total=False):
    community_id: str
    rule_id: Optional[str]
    initiative_id: Optional[str]

