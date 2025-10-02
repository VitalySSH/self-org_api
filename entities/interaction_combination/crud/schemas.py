from typing import TypedDict, List

from datastorage.crud.interfaces.schema import SchemaInstance


class ICAttributes(TypedDict):
    new_idea_description: str
    potential_impact: str
    reasoning: str


class ICRelations(TypedDict, total=False):
    interaction: SchemaInstance
    source_elements: List[SchemaInstance]


class ICRead(TypedDict):
    id: str
    attributes: ICAttributes
    relations: ICRelations


class ICCreate(TypedDict, total=False):
    id: str
    attributes: ICAttributes
    relations: ICRelations


class ICUpdate(ICCreate):
    pass
