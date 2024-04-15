from typing import TypedDict, TypeVar

from sqlalchemy.orm import DeclarativeBase

from datastorage.crud.interfaces.base import SchemaInstance

T = TypeVar('T', bound=DeclarativeBase)
InstanceSchema = TypeVar('InstanceSchema', bound=SchemaInstance)


class VotingParams(TypedDict):
    vote: int
    quorum: int


class PercentByName(TypedDict):
    percent: int
    name: str

