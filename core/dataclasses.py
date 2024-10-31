from dataclasses import dataclass


@dataclass
class BaseVotingParams:
    vote: int
    quorum: int
    significant_minority: int
