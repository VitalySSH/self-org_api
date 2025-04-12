from datetime import datetime, date
from typing import TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class InitiativeAttributes(TypedDict):
    title: str
    question: str
    content: str
    tracker: str
    is_one_day_event: bool
    is_extra_options: bool
    is_multi_select: bool
    community_id: str
    created: Optional[datetime]
    deadline: Optional[datetime]
    start_time: Optional[datetime]
    event_date: Optional[date]
    extra_question: Optional[str]


class InitiativeRelations(TypedDict, total=False):
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    voting_result: SchemaInstance
    responsible: SchemaInstance


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
