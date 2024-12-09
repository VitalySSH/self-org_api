from typing import List, TypedDict


class CreatingNewRule(TypedDict):
    title: str
    question: str
    content: str
    is_extra_options: str
    is_multi_select: str
    community_id: str
    category_id: str
    opinions: List[str]

