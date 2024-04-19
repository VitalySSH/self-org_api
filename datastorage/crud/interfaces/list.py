from enum import Enum
from typing import Union, List, Optional

from pydantic import BaseModel


class Direction(Enum):
    ASC = 'asc'
    DESC = 'desc'


class Operation(Enum):
    EQ = 'equals'
    IEQ = 'iequals'
    NOT_EQ = 'ne'
    NOT_IN = 'notin'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    IN = 'in'
    LIKE = 'like'
    ILIKE = 'ilike'
    BETWEEN = 'between'
    NULL = 'null'


class PaginationModel(BaseModel):
    skip: int
    limit: int


class Filter(BaseModel):
    field: str
    op: Operation
    val: Union[str, List[str], bool, int]


class Order(BaseModel):
    field: str
    direction: Direction


Filters = Optional[List[Filter]]
Orders = Optional[List[Order]]
Pagination = Optional[PaginationModel]


class ListData(BaseModel):
    filters: Filters = None
    orders: Orders = None
    pagination: Pagination = None
    include: Optional[List[str]] = None
