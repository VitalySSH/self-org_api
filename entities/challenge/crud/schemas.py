from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class ChallengeAttributes(TypedDict):
    title: str
    description: str
    community_id: str


class ChallengeRelations(TypedDict, total=False):
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    old_category: SchemaInstance
    solutions: List[SchemaInstance]


class ChallengeRead(TypedDict):
    id: str
    attributes: ChallengeAttributes
    relations: ChallengeRelations


class ChallengeCreate(TypedDict, total=False):
    id: str
    attributes: ChallengeAttributes
    relations: ChallengeRelations


class ChallengeUpdate(ChallengeCreate):
    pass
