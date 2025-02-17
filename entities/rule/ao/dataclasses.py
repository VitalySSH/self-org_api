from typing import List, TypedDict


class CreatingNewRule(TypedDict):
    title: str
    question: str
    content: str
    is_extra_options: bool
    is_multi_select: bool
    community_id: str
    category_id: str
    extra_options: List[str]

