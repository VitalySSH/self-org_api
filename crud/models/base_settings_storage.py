from typing import Optional

from pydantic import BaseModel

from crud.models.person import Person


class BaseSettingsValueStorage(BaseModel):
    id: Optional[str]
    value: Optional[str]
    creator: Optional[Person]
    community_id: Optional[str]
    type: Optional[str]
