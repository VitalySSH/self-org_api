from enum import Enum
from typing import TypeVar, Union, List, TypedDict

Object = TypeVar('Object')


class TypedDictNotTotal(TypedDict, total=False):
    pass


class Directions(Enum):
    ASC = 'asc'
    DESC = 'desc'


class Operations(Enum):
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
    CONTAINS = 'contains'
    BETWEEN = 'between'
    NULL = 'null'


class Pagination(TypedDictNotTotal):
    skip: int
    limit: int


class FilterItem(TypedDictNotTotal):
    field: str
    operation: Operations
    value: Union[str, List[str], bool]


class OrderItem(TypedDictNotTotal):
    field: str
    direction: Directions


Filters = List[FilterItem]
Orders = List[OrderItem]
