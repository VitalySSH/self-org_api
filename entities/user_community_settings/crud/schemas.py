from typing import List, TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class UserCsAttributes(TypedDict, total=False):
    community_id: str
    quorum: int
    vote: int
    significant_minority: int
    is_secret_ballot: Optional[bool]
    is_can_offer: Optional[bool]
    is_minority_not_participate: Optional[bool]
    is_not_delegate: Optional[bool]
    is_default_add_member: Optional[bool]
    is_blocked: bool


class UserCsRelations(TypedDict, total=False):
    user: SchemaInstance
    name: SchemaInstance
    description: SchemaInstance
    categories: List[SchemaInstance]
    sub_communities_settings: List[SchemaInstance]
    adding_members: List[SchemaInstance]


class UserCsRead(TypedDict):
    id: str
    attributes: UserCsAttributes
    relations: UserCsRelations


class UserCsCreate(TypedDict, total=False):
    id: str
    attributes: UserCsAttributes
    relations: UserCsRelations


class UserCsUpdate(UserCsCreate):
    pass
