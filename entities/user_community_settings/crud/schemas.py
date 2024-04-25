from typing import List, TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class UserCsAttributes(TypedDict, total=False):
    community_id: str
    quorum: int
    vote: int
    is_secret_ballot: bool
    is_can_offer: bool
    is_not_delegate: bool


class UserCsRelations(TypedDict, total=False):
    user: SchemaInstance
    name: SchemaInstance
    description: SchemaInstance
    init_categories: List[SchemaInstance]
    delegate_settings: List[SchemaInstance]
    adding_members: List[SchemaInstance]
    removal_members: List[SchemaInstance]


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
