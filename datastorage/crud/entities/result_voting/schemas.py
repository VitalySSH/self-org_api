from typing import TypedDict, List

from datastorage.crud.schemas.interfaces import SchemaInstance


class ResultVotingAttributes(TypedDict):
    vote: int


class ResultVotingRelations(TypedDict):
    member: SchemaInstance
    initiative: SchemaInstance


class ResultVotingRead(TypedDict, total=False):
    id: str
    attributes: ResultVotingAttributes
    relations: ResultVotingRelations


class ResultVotingCreate(TypedDict, total=False):
    id: str
    attributes: ResultVotingAttributes
    relations: ResultVotingRelations


class ResultVotingUpdate(ResultVotingCreate):
    pass
