from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.schema import SchemaInstance


class ResultVotingAttributes(TypedDict):
    vote: Optional[bool]
    member_id: str
    initiative_id: Optional[str]


class ResultVotingRelations(TypedDict, total=False):
    extra_options: List[SchemaInstance]


class ResultVotingRead(TypedDict):
    id: str
    attributes: ResultVotingAttributes
    relations: ResultVotingRelations


class ResultVotingCreate(TypedDict, total=False):
    id: str
    attributes: ResultVotingAttributes
    relations: ResultVotingRelations


class ResultVotingUpdate(ResultVotingCreate):
    pass
