from datetime import datetime
from typing import TypedDict, List

from datastorage.crud.interfaces.base import SchemaInstance


class CommunityAttributes(TypedDict):
    created: datetime


class CommunityRelations(TypedDict):
    main_settings: SchemaInstance
    creator: SchemaInstance
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
