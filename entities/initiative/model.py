from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, select, func, event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, Community
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        Status, Category, User, VotingResult
    )


class Initiative(Base):
    __tablename__ = TableName.INITIATIVE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    title: Mapped[str] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    is_one_day_event: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
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
    creator: Mapped['User'] = relationship(
        foreign_keys=f'{TableName.INITIATIVE}.c.creator_id',
        lazy='noload'
    )
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
    deadline: Mapped[datetime] = mapped_column(nullable=True)
    event_date: Mapped[date] = mapped_column(nullable=True)
    start_time: Mapped[datetime] = mapped_column(nullable=True)
    voting_result_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False,
        index=True,
    )
    voting_result: Mapped['VotingResult'] = relationship(
        uselist=False, lazy='noload')
    extra_question: Mapped[str] = mapped_column(nullable=True)
    responsible_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True,
        index=True,
    )
    responsible: Mapped['User'] = relationship(
        foreign_keys=f'{TableName.INITIATIVE}.c.responsible_id',
        lazy='noload'
    )
    tracker: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)

    @classmethod
    async def generate_tracker(
            cls,
            community_id: str,
            session: AsyncSession
    ) -> str:
        """Генерирует трекер для инициативы."""
        community = await session.get(Community, community_id)

        if community.parent_id is None:
            count = await session.scalar(
                select(func.count(cls.id))
                .where(cls.community_id == community_id)
            )
        else:
            count = await session.scalar(
                select(func.count(cls.id))
                .join(Community, cls.community_id == Community.id)
                .where(Community.parent_id == community.parent_id)
            )

        return f'{community.tracker}-И-{count + 1}'


@event.listens_for(Initiative, 'before_insert')
def before_insert_listener(mapper, connection, target):
    if target.tracker is None:
        connection.run_sync(
            lambda sync_conn: _async_before_insert(sync_conn, target)
        )


async def _async_before_insert(sync_conn, target):
    async with AsyncSession(bind=sync_conn, expire_on_commit=False) as session:
        target.tracker = await Initiative.generate_tracker(
            community_id=target.community_id,
            session=session,
        )
