from datetime import datetime
from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class SolutionAttributes(TypedDict, total=False):
    current_content: str
    status: str
    collective_influence_count: int
    is_author_like: Optional[bool]
    created_at: datetime
    updated_at: Optional[datetime]


class SolutionRelations(TypedDict, total=False):
    user: SchemaInstance
    challenge: SchemaInstance
    versions: List[SchemaInstance]
    interactions: List[SchemaInstance]


class SolutionRead(TypedDict):
    id: str
    attributes: SolutionAttributes
    relations: SolutionRelations


class SolutionCreate(TypedDict, total=False):
    id: str
    attributes: SolutionAttributes
    relations: SolutionRelations


class SolutionUpdate(SolutionCreate):
    pass
