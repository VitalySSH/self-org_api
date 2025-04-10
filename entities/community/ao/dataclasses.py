from dataclasses import dataclass
from typing import List, TypedDict, Tuple

from core.dataclasses import PercentByName
from entities.category.model import Category
from entities.responsibility.model import Responsibility
from entities.user_community_settings.model import UserCommunitySettings


@dataclass(kw_only=True)
class OtherCommunitySettings:
    categories: List[Category]
    sub_communities_settings: List[UserCommunitySettings]
    responsibilities: List[Responsibility]
    is_secret_ballot: bool
    is_minority_not_participate: bool
    is_can_offer: bool


@dataclass(kw_only=True)
class UserSettingsModifiedData:
    user_count: int
    categories_data: List[Tuple[str, int]]
    child_settings_data: List[Tuple[str, int]]
    responsibility_data: List[Tuple[str, int]]


class CsByPercent(TypedDict):
    names: List[PercentByName]
    descriptions: List[PercentByName]
    secret_ballot: List[PercentByName]
    minority_not_participate: List[PercentByName]
    can_offer: List[PercentByName]
    categories: List[PercentByName]
    sub_communities: List[PercentByName]
    responsibilities: List[PercentByName]


class ParentCommunity(TypedDict):
    id: str
    name: str


class CommunityNameData(TypedDict):
    name: str
    parent_data: List[ParentCommunity]
    is_blocked: bool


class SubCommunityData(TypedDict):
    id: str
    title: str
    description: str
    members: int
    isBlocked: bool
    isMyCommunity: bool
