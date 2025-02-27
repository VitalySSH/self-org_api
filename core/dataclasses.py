from dataclasses import dataclass
from typing import TypedDict


@dataclass
class BaseVotingParams:
    vote: int
    quorum: int
    significant_minority: int


@dataclass
class SimpleVoteResult:
    yes: int
    no: int
    abstain: int


class PercentByName(TypedDict):
    percent: int
    name: str
