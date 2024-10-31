from typing import List, TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class CSAttributes(TypedDict, total=False):
    quorum: Optional[int]
    vote: Optional[int]
    significant_minority: int
    is_secret_ballot: Optional[bool]
    is_can_offer: Optional[bool]
    is_minority_not_participate: Optional[bool]


class CSRelations(TypedDict, total=False):
    name: Optional[SchemaInstance]
    description: Optional[SchemaInstance]
    categories: List[SchemaInstance]
    adding_members: List[SchemaInstance]


class ReadComSettings(TypedDict):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class CreateComSettings(TypedDict, total=False):
    id: str
    attributes: CSAttributes
    relations: CSRelations


class UpdateComSettings(CreateComSettings):
    pass
