from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import Status, Category, User, Solution


class Challenge(Base):
    __tablename__ = TableName.CHALLENGE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
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
    category: Mapped['Category'] = relationship(
        lazy='noload',
        foreign_keys=[category_id],
    )
    old_category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CATEGORY}.id'),
        nullable=True,
    )
    old_category: Mapped['Category'] = relationship(
        lazy='noload',
        foreign_keys=[old_category_id]
    )
    solutions: Mapped[List['Solution']] = relationship(
        back_populates='challenge',
        lazy='noload'
    )
