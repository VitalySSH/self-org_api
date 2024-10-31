from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class VResultAttributes(TypedDict):
    vote: Optional[bool]
    is_significant_minority: Optional[bool]


class VResultRelations(TypedDict, total=False):
    selected_options: List[SchemaInstance]


class VResultRead(TypedDict):
    id: str
    attributes: VResultAttributes
    relations: VResultRelations


class VResultCreate(TypedDict, total=False):
    id: str
    attributes: VResultAttributes
    relations: VResultRelations


class VResultUpdate(VResultCreate):
    pass
