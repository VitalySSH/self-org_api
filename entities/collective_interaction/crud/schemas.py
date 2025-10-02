from datetime import datetime
from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class CIAttributes(TypedDict):
    interaction_type: str
    user_response: str
    user_reasoning: Optional[str]
    applied_to_solution: bool
    created_at: Optional[datetime]
    responded_at: Optional[datetime]


class CIRelations(TypedDict, total=False):
    solution: SchemaInstance
    suggestions: List[SchemaInstance]
    criticisms: List[SchemaInstance]
    combinations: List[SchemaInstance]
    influences: List[SchemaInstance]


class CIRead(TypedDict):
    id: str
    attributes: CIAttributes
    relations: CIRelations


class CICreate(TypedDict, total=False):
    id: str
    attributes: CIAttributes
    relations: CIRelations


class CIUpdate(CICreate):
    pass
