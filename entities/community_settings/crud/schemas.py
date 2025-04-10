from typing import List, TypedDict, Optional

from datastorage.crud.interfaces.schema import SchemaInstance


class LastVotingParams(TypedDict, total=False):
    vote: int
    quorum: int
    significant_minority: int


class CSAttributes(TypedDict, total=False):
    quorum: Optional[int]
    vote: Optional[int]
    significant_minority: int
    decision_delay: int
    dispute_time_limit: int
    is_secret_ballot: Optional[bool]
    is_can_offer: Optional[bool]
    is_minority_not_participate: Optional[bool]


class CSRelations(TypedDict, total=False):
    name: Optional[SchemaInstance]
    description: Optional[SchemaInstance]
    categories: List[SchemaInstance]
    sub_communities_settings: List[SchemaInstance]
    responsibilities: List[SchemaInstance]


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
