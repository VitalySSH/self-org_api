from datetime import datetime
from typing import TypedDict, List, Optional

from datastorage.crud.schemas.interfaces import SchemaInstance


class InitiativeAttributes(TypedDict):
    content: str
    deadline: datetime
    likes_count: Optional[int]
    dislikes_count: Optional[int]
    current_user_like: Optional[bool]


class InitiativeRelations(TypedDict):
    type: SchemaInstance
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    voting_results: List[SchemaInstance]
    opinions: List[SchemaInstance]


class InitiativeRead(TypedDict):
    id: str
    attributes: InitiativeAttributes
    relations: InitiativeRelations


class InitiativeCreate(TypedDict, total=False):
    id: str
    attributes: InitiativeAttributes
    relations: InitiativeRelations


class InitiativeUpdate(InitiativeCreate):
    pass
