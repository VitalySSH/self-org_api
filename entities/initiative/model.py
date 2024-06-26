from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, InitiativeCategory, User, InitiativeType, VotingResult, Opinion, Like
    )


class Initiative(Base):
    __tablename__ = TableName.INITIATIVE

    EXCLUDE_READ_FIELDS = ['likes']

    content: Mapped[str] = mapped_column(nullable=False)
    type_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_TYPE}.id'),
        nullable=False,
        index=True,
    )
    type: Mapped['InitiativeType'] = relationship(lazy='noload')
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
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id'),
        nullable=False,
        index=True,
    )
    category: Mapped['InitiativeCategory'] = relationship(lazy='noload')
    deadline: Mapped[datetime] = mapped_column(default=datetime.now)
    voting_results: Mapped[List['VotingResult']] = relationship(
        secondary=TableName.RELATION_INITIATIVE_VR, lazy='noload')
    opinions: Mapped[List['Opinion']] = relationship(
        secondary=TableName.RELATION_INITIATIVE_OPINION, lazy='noload')
    likes: Mapped[List['Like']] = relationship(
        secondary=TableName.RELATION_INITIATIVE_LIKE, lazy='noload')
