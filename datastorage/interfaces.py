from typing import TypedDict, TypeVar

from datastorage.database.models import Base

T = TypeVar('T', bound=Base)


class RelationRow(TypedDict):
    id: str
    from_id: str
    to_id: str
