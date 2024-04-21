from typing import TypedDict, TypeVar, List

from datastorage.database.models import Base

T = TypeVar('T', bound=Base)


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
    can_offer: List[PercentByName]
    categories: List[PercentByName]
