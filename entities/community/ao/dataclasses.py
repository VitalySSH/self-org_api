from dataclasses import dataclass
from typing import List

from entities.initiative_category.model import InitiativeCategory


@dataclass
class OtherCommunitySettings:
    categories: List[InitiativeCategory]
    is_secret_ballot: bool
    is_minority_not_participate: bool
    is_can_offer: bool
