from typing import TypedDict, List

from datastorage.crud.schemas.interfaces import SchemaInstance


class LikeAttributes(TypedDict):
    is_like: bool
    quorum: int
    vote: int


class LikeRelations(TypedDict):
    creator: SchemaInstance
    initiative: SchemaInstance
    opinion: SchemaInstance
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
