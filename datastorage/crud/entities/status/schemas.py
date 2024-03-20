from typing import Union

from pydantic import BaseModel

from datastorage.crud.schemas.base import BaseUpdateScheme, DirtyAttribute, dirty_attribute


class ReadStatus(BaseModel):
    id: str
    code: str
    name: str

    class Config:
        from_attributes = True


class CreateStatus(BaseModel):
    code: str
    name: str


class UpdateStatus(BaseUpdateScheme):
    code: Union[str, None, DirtyAttribute] = dirty_attribute
    name: Union[str, None, DirtyAttribute] = dirty_attribute
