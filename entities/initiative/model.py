from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, Category, User, UserVotingResult, Opinion, VotingOption, VotingResult
    )


class Initiative(Base):
    __tablename__ = TableName.INITIATIVE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
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
    creator: Mapped['User'] = relationship(
        foreign_keys=f'{TableName.INITIATIVE}.c.creator_id',
        lazy='noload'
    )
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
    deadline: Mapped[datetime] = mapped_column(default=datetime.now)
    voting_result_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False,
        index=True,
    )
    voting_result: Mapped['VotingResult'] = relationship(uselist=False, lazy='noload')
    extra_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_INITIATIVE_OPTIONS, lazy='noload')
    user_results: Mapped[List['UserVotingResult']] = relationship(
        secondary=TableName.RELATION_INITIATIVE_USER_VR, lazy='noload')
    responsible_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True,
        index=True,
    )
    responsible: Mapped['User'] = relationship(
        foreign_keys=f'{TableName.INITIATIVE}.c.responsible_id',
        lazy='noload'
    )
