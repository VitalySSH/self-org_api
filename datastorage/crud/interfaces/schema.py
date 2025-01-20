from typing import TypedDict, Dict, Any, Union, List, TypeVar, Generic

S = TypeVar('S')


class RelationsSchema(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Any]


Relations = Dict[str, Union[RelationsSchema, List[RelationsSchema]]]


class SchemaReadInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Relations


class SchemaInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Relations


class ListResponseSchema(TypedDict, Generic[S]):
    items: List[S]
    total: int
