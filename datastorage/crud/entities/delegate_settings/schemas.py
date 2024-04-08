from typing import List, TypedDict

from datastorage.crud.schemas.interfaces import SchemaInstance


class DelegateSettingsRelations(TypedDict, total=False):
    user: SchemaInstance
    community: SchemaInstance
    init_categories: List[SchemaInstance]


class DelegateSettingsRead(TypedDict):
    id: str
    relations: DelegateSettingsRelations


class DelegateSettingsCreate(TypedDict, total=False):
    id: str
    relations: DelegateSettingsRelations


class DelegateSettingsUpdate(DelegateSettingsCreate):
    pass
