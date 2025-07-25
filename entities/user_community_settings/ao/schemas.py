from typing import List, TypedDict, Optional


class InitCategoryData(TypedDict):
    name: str


class SettingDataToCreate(TypedDict, total=False):
    names: List[str]
    descriptions: List[str]
    categories: List[InitCategoryData]
    quorum: int
    vote: int
    significant_minority: int
    decision_delay: int
    dispute_time_limit: int
    is_workgroup: bool
    workgroup: Optional[int]
    is_secret_ballot: Optional[bool]
    is_can_offer: Optional[bool]
    is_minority_not_participate: Optional[bool]
    is_not_delegate: Optional[bool]
    is_default_add_member: Optional[bool]


class ChildSettingDataToCreate(SettingDataToCreate, total=False):
    parent_community_id: str
