from dataclasses import dataclass
from typing import List, TypedDict

from core.dataclasses import PercentByName
from entities.category.model import Category


@dataclass
class OtherCommunitySettings:
    categories: List[Category]
    is_secret_ballot: bool
    is_minority_not_participate: bool
    is_can_offer: bool


class CsByPercent(TypedDict):
    names: List[PercentByName]
    descriptions: List[PercentByName]
    secret_ballot: List[PercentByName]
    minority_not_participate: List[PercentByName]
    can_offer: List[PercentByName]
    categories: List[PercentByName]
