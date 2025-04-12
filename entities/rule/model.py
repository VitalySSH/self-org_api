from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, select, func, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, Community
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, Category, User, VotingResult
    )


class Rule(Base):
    __tablename__ = TableName.RULE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    title: Mapped[str] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    is_extra_options: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    is_multi_select: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    created: Mapped[datetime] = mapped_column(default=datetime.now)
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
    start_time: Mapped[datetime] = mapped_column(nullable=True)
    voting_result_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False,
        index=True,
    )
    voting_result: Mapped['VotingResult'] = relationship(
        uselist=False, lazy='noload'
    )
    extra_question: Mapped[str] = mapped_column(nullable=True)
    tracker: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)


@event.listens_for(Rule, 'before_insert')
def before_insert_listener(mapper, connection, target):
    if target.tracker is None:

        if target.community_id:
            community = connection.execute(
                select(Community).where(Community.id == target.community_id)
            ).first()

            if community.parent_id is None:
                count = connection.execute(
                    select(func.count(Rule.id))
                    .where(Rule.community_id == target.community_id)
                ).scalar()
                tracker = f'П-{count + 1}'
            else:
                count = connection.execute(
                    select(func.count(Rule.id))
                    .join(Community, Rule.community_id == Community.id)
                    .where(Community.parent_id == community.parent_id)
                ).scalar()
                tracker = f'{community.tracker}/П-{count + 1}'

            target.tracker = tracker
