from typing import TypedDict


class StatusAttributes(TypedDict, total=False):
    code: str
    name: str


class StatusRead(TypedDict):
    id: str
    attributes: StatusAttributes


class StatusCreate(TypedDict, total=False):
    id: str
    attributes: StatusAttributes


class StatusUpdate(StatusCreate):
    pass
