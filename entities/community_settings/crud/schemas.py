from typing import List, TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class CSAttributes(TypedDict):
    quorum: int
    vote: int
    is_secret_ballot: bool
    is_can_offer: bool


class CSRelations(TypedDict, total=False):
    name: SchemaInstance
    description: SchemaInstance
    init_categories: List[SchemaInstance]


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
