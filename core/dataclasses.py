from dataclasses import dataclass
from typing import TypedDict


@dataclass
class BaseVotingParams:
    vote: int
    quorum: int
    significant_minority: int


class PercentByName(TypedDict):
    percent: int
    name: str
