from datetime import datetime
from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class InitiativeAttributes(TypedDict):
    title: str
    question: str
    content: str
    is_extra_options: bool
    is_multi_select: bool
    community_id: str
    deadline: datetime


class InitiativeRelations(TypedDict, total=False):
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    extra_options: List[SchemaInstance]
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
