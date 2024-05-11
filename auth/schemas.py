from typing import Optional

from pydantic import BaseModel


class CurrentUser(BaseModel):
    firstname: str
    surname: str
    foto_id: Optional[str]
    email: str
    hashed_password: str
