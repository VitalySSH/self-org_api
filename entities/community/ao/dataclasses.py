from dataclasses import dataclass
from typing import List, TypedDict, Tuple

from core.dataclasses import PercentByName
from entities.category.model import Category
from entities.user_community_settings.model import UserCommunitySettings


@dataclass
class OtherCommunitySettings:
    categories: List[Category]
    sub_communities_settings: List[UserCommunitySettings]
    is_secret_ballot: bool
    is_minority_not_participate: bool
    is_can_offer: bool


@dataclass
class UserSettingsModifiedData:
    user_count: int
    categories_data: List[Tuple[str, int]]
    child_settings_data: List[Tuple[str, int]]


class CsByPercent(TypedDict):
    names: List[PercentByName]
    descriptions: List[PercentByName]
    secret_ballot: List[PercentByName]
    minority_not_participate: List[PercentByName]
    can_offer: List[PercentByName]
    categories: List[PercentByName]
    sub_communities: List[PercentByName]


class CommunityNameData(TypedDict):
    name: str
    parent_ids: List[str]
