from typing import List, TypedDict

from datastorage.crud.interfaces.schema import SchemaInstance


class DelegateSettingsAttributes(TypedDict):
    user_id: str


class DelegateSettingsRelations(TypedDict, total=False):
    category: SchemaInstance
    delegates: List[SchemaInstance]


class DelegateSettingsRead(TypedDict):
    id: str
    attributes: DelegateSettingsAttributes
    relations: DelegateSettingsRelations


class DelegateSettingsCreate(TypedDict, total=False):
    id: str
    attributes: DelegateSettingsAttributes
    relations: DelegateSettingsRelations


class DelegateSettingsUpdate(DelegateSettingsCreate):
    pass
