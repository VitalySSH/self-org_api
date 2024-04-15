from typing import TypedDict, List, Optional

from datastorage.crud.interfaces.base import SchemaInstance


class LikeAttributes(TypedDict):
    is_like: bool
    creator_id: str
    initiative_id: Optional[str]
    opinion_id: Optional[str]


class LikeRelations(TypedDict):
    initiatives_set: List[SchemaInstance]
    opinions_set: List[SchemaInstance]


class LikeRead(TypedDict):
    id: str
    attributes: LikeAttributes
    relations: LikeRelations


class LikeCreate(TypedDict, total=False):
    id: str
    attributes: LikeAttributes
    relations: LikeRelations


class LikeUpdate(LikeCreate):
    pass
