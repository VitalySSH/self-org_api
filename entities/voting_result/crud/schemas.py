from typing import TypedDict, Optional


class VResultAttributes(TypedDict):
    vote: Optional[bool]
    is_significant_minority: Optional[bool]
    options: str
    minority_options: str


class VResultRead(TypedDict):
    id: str
    attributes: VResultAttributes


class VResultCreate(TypedDict, total=False):
    id: str
    attributes: VResultAttributes


class VResultUpdate(VResultCreate):
    pass
