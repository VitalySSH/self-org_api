from datetime import datetime
from typing import TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class RequestMemberAttributes(TypedDict, total=False):
    vote: Optional[bool]
    reason: Optional[str]
    parent_id: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]


class RequestMemberRelations(TypedDict, total=False):
    member: SchemaInstance
    creator: SchemaInstance
    community: SchemaInstance
    status: SchemaInstance


class RequestMemberRead(TypedDict):
    id: str
    attributes: RequestMemberAttributes
    relations: RequestMemberRelations


class RequestMemberCreate(TypedDict, total=False):
    id: str
    attributes: RequestMemberAttributes
    relations: RequestMemberRelations


class RequestMemberUpdate(RequestMemberCreate):
    pass
