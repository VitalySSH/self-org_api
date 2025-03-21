from typing import List, TypedDict, Optional


class CreatingNewInitiative(TypedDict, total=False):
    title: str
    question: str
    content: str
    is_one_day_event: bool
    event_date: Optional[str]
    is_extra_options: bool
    is_multi_select: bool
    community_id: str
    category_id: str
    extra_question: Optional[str]
    extra_options: List[str]
