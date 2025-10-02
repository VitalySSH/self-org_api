from typing import TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class ICrAttributes(TypedDict):
    criticism_text: str
    severity: str
    suggested_fix: str
    reasoning: str


class ICrRelations(TypedDict, total=False):
    interaction: SchemaInstance


class ICrRead(TypedDict):
    id: str
    attributes: ICrAttributes
    relations: ICrRelations


class ICrCreate(TypedDict, total=False):
    id: str
    attributes: ICrAttributes
    relations: ICrRelations


class ICrUpdate(ICrCreate):
    pass
