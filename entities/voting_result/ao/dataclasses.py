from typing import TypedDict


class SimpleVoteResult(TypedDict):
    yes: int
    no: int
    abstain: int
