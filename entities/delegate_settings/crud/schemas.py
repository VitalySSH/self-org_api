from typing import List, TypedDict

from datastorage.crud.interfaces.base import SchemaInstance


class DelegateSettingsRelations(TypedDict, total=False):
    user: SchemaInstance
    init_category: SchemaInstance
    delegates: List[SchemaInstance]


class DelegateSettingsRead(TypedDict):
    id: str
    relations: DelegateSettingsRelations


class DelegateSettingsCreate(TypedDict, total=False):
    id: str
    relations: DelegateSettingsRelations


class DelegateSettingsUpdate(DelegateSettingsCreate):
    pass
