from dataclasses import dataclass
from typing import List, Optional

from entities.community_description.model import CommunityDescription
from entities.community_name.model import CommunityName
from entities.category.model import Category
from auth.models.user import User
from entities.user_community_settings.crud.schemas import UserCsAttributes


@dataclass(kw_only=True)
class CreatingCommunity:
    name: str
    description: str
    category_names: List[str]
    settings: UserCsAttributes
    user: User
    community_id: Optional[str] = None
    parent_community_id: Optional[str] = None
    name_obj: Optional[CommunityName] = None
    description_obj: Optional[CommunityDescription] = None
    categories_objs: Optional[List[Category]] = None
