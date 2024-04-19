from typing import TypedDict, Dict, Any, Union, List, TypeVar

S = TypeVar('S')


class RelationsSchema(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Any]


class SchemaReadInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    read_only: Dict[str, Any]
    relations: Dict[str, Union[RelationsSchema, List[RelationsSchema]]]


class SchemaInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Union[RelationsSchema, List[RelationsSchema]]]