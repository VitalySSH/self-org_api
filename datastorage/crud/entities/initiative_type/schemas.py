from typing import TypedDict


class InitiativeTypeAttributes(TypedDict):
    name: str
    code: str


class InitiativeTypeRead(TypedDict):
    id: str
    attributes: InitiativeTypeAttributes


class InitiativeTypeCreate(TypedDict, total=False):
    id: str
    attributes: InitiativeTypeAttributes


class InitiativeTypeUpdate(InitiativeTypeCreate):
    pass
