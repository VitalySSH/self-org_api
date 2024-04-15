from typing import TypedDict, Optional, List

from datastorage.crud.interfaces.base import SchemaInstance


class ResultVotingAttributes(TypedDict):
    member_id: str
    initiative_id: Optional[str]


class ResultVotingRelations(TypedDict):
    only_option: SchemaInstance
    multiple_options: List[SchemaInstance]


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
