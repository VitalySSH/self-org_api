from typing import TypedDict, Dict, Any, Union, List


class RelationsSchema(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Any]


class SchemaInstance(TypedDict, total=False):
    id: str
    attributes: Dict[str, Any]
    relations: Dict[str, Union[RelationsSchema, List[RelationsSchema]]]
