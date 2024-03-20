from typing import Union

from pydantic import BaseModel

from datastorage.crud.entities.status.schemas import ReadStatus
from datastorage.crud.schemas.base import BaseUpdateScheme, DirtyAttribute, dirty_attribute


class BaseIC(BaseModel):
    name: str
    creator: str


class ReadIC(BaseIC):
    id: str
    status: ReadStatus

    class Config:
        from_attributes = True


class CreateIC(BaseIC):
    status: str


class UpdateIC(BaseUpdateScheme):
    name: Union[str, DirtyAttribute] = dirty_attribute
    creator: Union[str, DirtyAttribute] = dirty_attribute
    status: Union[str, DirtyAttribute] = dirty_attribute
