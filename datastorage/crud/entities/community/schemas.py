from datetime import datetime
from typing import TypedDict, List

from datastorage.crud.schemas.interfaces import SchemaInstance


class CSAttributes(TypedDict):
    name: str
    quorum: int
    vote: int


class CSRelations(TypedDict):
    user: SchemaInstance
    community: SchemaInstance
    init_categories: List[SchemaInstance]


class ReadComSettings(TypedDict):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class CommunityReadAttributes(TypedDict):
    created: datetime


class CommunityRelations(TypedDict, total=False):
    main_settings: SchemaInstance
    creator: SchemaInstance


class CommunityRead(TypedDict, total=False):
    id: str
    attributes: CommunityReadAttributes
    relations: CommunityRelations


class CommunityCreate(TypedDict, total=False):
    id: str
    relations: CommunityRelations


class CommunityUpdate(CommunityCreate):
    pass
