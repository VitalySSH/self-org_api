from datetime import datetime
from typing import TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class RuleAttributes(TypedDict):
    title: str
    question: str
    extra_question: Optional[str]
    content: str
    tracker: str
    is_extra_options: bool
    is_multi_select: bool
    community_id: str
    start_time: Optional[datetime]
    created: Optional[datetime]


class RuleRelations(TypedDict, total=False):
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    voting_result: SchemaInstance


class RuleRead(TypedDict):
    id: str
    attributes: RuleAttributes
    relations: RuleRelations


class RuleCreate(TypedDict, total=False):
    id: str
    attributes: RuleAttributes
    relations: RuleRelations


class RuleUpdate(RuleCreate):
    pass
