from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileMetaRead(BaseModel):
    id: str
    name: str
    mimetype: str
    created: datetime
    updated: Optional[datetime]
