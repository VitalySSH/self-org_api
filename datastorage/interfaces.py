from typing import TypedDict, TypeVar

from sqlalchemy.orm import DeclarativeBase


T = TypeVar('T', bound=DeclarativeBase)
SchemaInstanceAbstract = TypeVar('SchemaInstanceAbstract')
InitiativeCategory = TypeVar('InitiativeCategory')


class VotingParams(TypedDict):
    vote: int
    quorum: int


class PercentByName(TypedDict):
    percent: int
    name: str

