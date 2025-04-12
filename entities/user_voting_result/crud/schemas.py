from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class UserVRAttributes(TypedDict):
    vote: Optional[bool]
    is_voted_myself: Optional[bool]
    is_voted_by_default: Optional[bool]
    member_id: str
    community_id: str
    initiative_id: Optional[str]
    rule_id: Optional[str]
    is_blocked: Optional[bool]


class UserVRRelations(TypedDict, total=False):
    voting_result: SchemaInstance
    extra_options: List[SchemaInstance]
    noncompliance: List[SchemaInstance]


class UserVRRead(TypedDict):
    id: str
    attributes: UserVRAttributes
    relations: UserVRRelations


class UserVRCreate(TypedDict, total=False):
    id: str
    attributes: UserVRAttributes
    relations: UserVRRelations


class UserVRUpdate(UserVRCreate):
    pass
