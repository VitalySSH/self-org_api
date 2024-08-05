from typing import TypedDict, TypeVar, List

from datastorage.database.models import Base

T = TypeVar('T', bound=Base)


class RelationRow(TypedDict):
    id: str
    from_id: str
    to_id: str


class VotingParams(TypedDict):
    vote: int
    quorum: int


class PercentByName(TypedDict):
    percent: int
    name: str


class CsByPercent(TypedDict):
    names: List[PercentByName]
    descriptions: List[PercentByName]
    secret_ballot: List[PercentByName]
    minority_not_participate: List[PercentByName]
    can_offer: List[PercentByName]
    categories: List[PercentByName]
