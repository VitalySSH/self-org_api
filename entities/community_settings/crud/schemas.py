from typing import List, TypedDict

from datastorage.crud.interfaces.base import SchemaInstance


class CSAttributes(TypedDict):
    name: str
    quorum: int
    vote: int
    is_secret_ballot: bool
    is_can_offer: bool


class CSRelations(TypedDict, total=False):
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
