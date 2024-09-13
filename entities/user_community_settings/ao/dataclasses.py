from dataclasses import dataclass
from typing import List, Optional

from entities.community.model import Community
from entities.community_description.model import CommunityDescription
from entities.community_name.model import CommunityName
from entities.initiative_category.model import InitiativeCategory
from entities.user.model import User
from entities.user_community_settings.crud.schemas import UserCsAttributes


@dataclass
class CreatingCommunity:
    name: str
    description: str
    init_categories: List[str]
    settings: UserCsAttributes
    user: User
    community_id: Optional[str] = None
    name_obj: Optional[CommunityName] = None
    description_obj: Optional[CommunityDescription] = None
    init_categories_objs: Optional[List[InitiativeCategory]] = None
    community_obj: Optional[Community] = None
