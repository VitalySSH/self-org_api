from dataclasses import dataclass
from typing import TypedDict


@dataclass(kw_only=True)
class BaseVotingParams:
    vote: int
    quorum: int
    significant_minority: int


@dataclass(kw_only=True)
class SimpleVoteResult:
    yes: int
    no: int
    abstain: int


@dataclass(kw_only=True)
class BaseTimeParams:
    decision_delay: int
    dispute_time_limit: int


class PercentByName(TypedDict):
    percent: int
    name: str
