from datetime import datetime
from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class InitiativeAttributes(TypedDict):
    content: str
    deadline: datetime


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
