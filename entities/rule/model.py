from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, Category, User, UserVotingResult, Opinion, VotingOption, VotingResult
    )


class Rule(Base):
    __tablename__ = TableName.RULE

    title: Mapped[str] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    is_extra_options: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_multi_select: Mapped[bool] = mapped_column(nullable=False, default=False)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    status_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id'),
        nullable=False,
        index=True,
    )
    status: Mapped['Status'] = relationship(lazy='noload')
    category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CATEGORY}.id'),
        nullable=False,
        index=True,
    )
    category: Mapped['Category'] = relationship(lazy='noload')
    voting_result_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False,
        index=True,
    )
    voting_result: Mapped['VotingResult'] = relationship(uselist=False, lazy='noload')
    extra_question: Mapped[str] = mapped_column(nullable=True)
    extra_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_RULE_OPTIONS, lazy='noload')
    user_results: Mapped[List['UserVotingResult']] = relationship(
        secondary=TableName.RELATION_RULE_USER_VR, lazy='noload')
    opinions: Mapped[List['Opinion']] = relationship(
        secondary=TableName.RELATION_RULE_OPINION, lazy='noload')
