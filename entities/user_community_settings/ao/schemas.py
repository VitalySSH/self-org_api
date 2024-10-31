from typing import List, TypedDict, Optional


class InitCategoryData(TypedDict):
    name: str


class UpdatingDataAfterJoin(TypedDict):
    user_settings_id: str
    community_id: str
    request_member_id: str


class SettingDataToCreate(TypedDict, total=False):
    name: str
    description: str
    categories: List[InitCategoryData]
    quorum: int
    vote: int
    significant_minority: int
    is_secret_ballot: Optional[bool]
    is_can_offer: Optional[bool]
    is_minority_not_participate: Optional[bool]
    is_not_delegate: Optional[bool]
    is_default_add_member: Optional[bool]
