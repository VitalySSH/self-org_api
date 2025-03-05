from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import VotingOption, VotingResult


class UserVotingResult(Base):
    __tablename__ = TableName.USER_VOTING_RESULT

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    vote: Mapped[bool] = mapped_column(nullable=True)
    extra_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_USER_VR_VO, lazy='noload'
    )
    is_voted_myself: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    member_id: Mapped[str] = mapped_column(nullable=True, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    voting_result_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False,
        index=True,
    )
    voting_result: Mapped['VotingResult'] = relationship(lazy='noload')
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
    rule_id: Mapped[str] = mapped_column(nullable=True, index=True)
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
