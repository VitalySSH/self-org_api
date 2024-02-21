from enum import Enum
from typing import Union, List, TypedDict


class TypedDictNotTotal(TypedDict, total=False):
    pass


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


class Pagination(TypedDictNotTotal):
    skip: int
    limit: int


class Filter(TypedDictNotTotal):
    field: str
    op: Operation
    val: Union[str, List[str], bool, int]


class Order(TypedDictNotTotal):
    field: str
    direction: Direction


Filters = List[Filter]
Orders = List[Order]
