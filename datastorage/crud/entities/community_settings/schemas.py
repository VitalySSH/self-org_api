from typing import Optional, Union

from pydantic import BaseModel

from auth.user.schemas import ReadUser
from datastorage.schemas.base import BaseUpdateScheme, DirtyAttribute, dirty_attribute


class BaseCS(BaseModel):
    name: str
    quorum: int
    vote: int


class ReadCS(BaseCS):
    id: str
    user: Optional[ReadUser]
    community: Optional[str]

    class Config:
        from_attributes = True


class CreateCS(BaseCS):
    user: Optional[str] = None
    community: Optional[str] = None


class UpdateCS(BaseUpdateScheme):
    name: Union[str, DirtyAttribute] = dirty_attribute
    quorum: Union[int, DirtyAttribute] = dirty_attribute
    vote: Union[int, DirtyAttribute] = dirty_attribute
    user: Union[str, None, DirtyAttribute] = dirty_attribute
    community: Union[str, None, DirtyAttribute] = dirty_attribute
