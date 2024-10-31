from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class UserVRAttributes(TypedDict):
    vote: Optional[bool]
    member_id: str
    initiative_id: Optional[str]


class UserVRRelations(TypedDict, total=False):
    extra_options: List[SchemaInstance]


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
