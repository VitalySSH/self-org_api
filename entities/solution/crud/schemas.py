from typing import TypedDict


class SolutionAttributes(TypedDict):
    text: str
    creator_id: str


class SolutionRead(TypedDict):
    id: str
    attributes: SolutionAttributes


class SolutionCreate(TypedDict, total=False):
    id: str
    attributes: SolutionAttributes


class SolutionUpdate(SolutionCreate):
    pass
