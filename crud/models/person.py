from typing import Optional, List

from pydantic import BaseModel

from crud.models.user import User


class Person(BaseModel):
    id: Optional[str]
    user_id: Optional[User]
    name: Optional[str]
    surname: Optional[str]
    delegates: List['Person']
    observed_persons: List['Person']
