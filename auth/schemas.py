from typing import Optional

from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str
    firstname: str
    surname: str
    about_me: Optional[str]
    foto_id: Optional[str]
    email: str
