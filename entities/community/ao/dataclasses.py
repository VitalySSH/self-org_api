from dataclasses import dataclass
from typing import List

from entities.category.model import Category


@dataclass
class OtherCommunitySettings:
    categories: List[Category]
    is_secret_ballot: bool
    is_minority_not_participate: bool
    is_can_offer: bool
