from datetime import datetime
from typing import TypedDict, List, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class CommunityAttributes(TypedDict, total=False):
    is_blocked: Optional[bool]
    created: datetime


class CommunityRelations(TypedDict, total=False):
    main_settings: SchemaInstance
    creator: SchemaInstance
    parent: SchemaInstance
    user_settings: List[SchemaInstance]


class CommunityRead(TypedDict):
    id: str
    attributes: CommunityAttributes
    relations: CommunityRelations


class CommunityCreate(TypedDict, total=False):
    id: str
    relations: CommunityRelations


class CommunityUpdate(CommunityCreate):
    pass
