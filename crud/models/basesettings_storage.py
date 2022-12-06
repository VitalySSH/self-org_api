from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from crud.models.person import Person


class BaseSettingsStorage(BaseModel):
    id: Optional[str]
    value: Optional[str]
    creator: Optional[Person]
    community_id: Optional[str]
    voting_id: Optional[str]
