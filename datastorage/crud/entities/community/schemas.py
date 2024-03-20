from datetime import datetime
from typing import Union

from pydantic import BaseModel

from datastorage.crud.entities.community_settings.schemas import ReadCS
from datastorage.crud.entities.user.schemas import ReadUser
from datastorage.crud.schemas.base import BaseUpdateScheme, DirtyAttribute, dirty_attribute


class ReadCommunity(BaseModel):
    id: str
    main_settings: ReadCS
    creator: ReadUser
    created: datetime

    class Config:
        from_attributes = True


class CreateCommunity(BaseModel):
    main_settings: str
    creator: str


class UpdateCommunity(BaseUpdateScheme):
    main_settings: Union[str, None, DirtyAttribute] = dirty_attribute
    creator: Union[str, None, DirtyAttribute] = dirty_attribute
