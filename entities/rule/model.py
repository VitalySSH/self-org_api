from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, Category, User, VotingResult, Opinion, VotingOption
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
    extra_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_RULE_OPTIONS, lazy='noload')
    voting_results: Mapped[List['VotingResult']] = relationship(
        secondary=TableName.RELATION_RULE_VR, lazy='noload')
    opinions: Mapped[List['Opinion']] = relationship(
        secondary=TableName.RELATION_RULE_OPINION, lazy='noload')
