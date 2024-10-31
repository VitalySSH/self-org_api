from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class RuleAttributes(TypedDict):
    title: str
    question: str
    content: str
    is_extra_options: bool
    is_multi_select: bool
    community_id: str


class RuleRelations(TypedDict, total=False):
    creator: SchemaInstance
    status: SchemaInstance
    category: SchemaInstance
    extra_options: List[SchemaInstance]
    user_results: List[SchemaInstance]
    opinions: List[SchemaInstance]


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
