from typing import TypedDict, TypeVar

SchemaInstance = TypeVar('SchemaInstance')


class VotingParams(TypedDict):
    vote: int
    quorum: int


class PercentByName(TypedDict):
    percent: int
    name: str

