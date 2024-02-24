from typing import Optional

from pydantic import BaseModel

from auth.user.schemas import ReadUser


class BaseCS(BaseModel):
    name: str
    quorum: int
    vote: int


class ReadCS(BaseCS):
    id: str
    user: Optional[ReadUser]

    class Config:
        from_attributes = True


class CreateCS(BaseCS):
    user: Optional[str] = None
    community: Optional[str] = None
