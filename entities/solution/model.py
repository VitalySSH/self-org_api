from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid
from entities.solution.crud.enums import SolutionStatus


if TYPE_CHECKING:
    from datastorage.database.models import (
        Challenge, SolutionVersion, CollectiveInteraction, User
    )


class Solution(Base):
    __tablename__ = TableName.SOLUTION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    challenge_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CHALLENGE}.id'),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True
    )
    current_content: Mapped[str] = mapped_column(nullable=False, default="")
    status: Mapped[str] = mapped_column(
        nullable=False,
        default=SolutionStatus.DRAFT.value,
    )
    collective_influence_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )
    is_author_like: Mapped[bool] = mapped_column(nullable=True, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now
    )

    # Relationships
    user: Mapped['User'] = relationship(lazy='noload')
    challenge: Mapped['Challenge'] = relationship(
        back_populates='solutions',
        lazy='noload'
    )
    versions: Mapped[List['SolutionVersion']] = relationship(
        back_populates='solution',
        lazy='noload'
    )
    interactions: Mapped[List['CollectiveInteraction']] = relationship(
        back_populates='solution',
        lazy='noload'
    )

    __table_args__ = (
        UniqueConstraint(
            'challenge_id', 'user_id', name='uq_task_user_solution'
        ),
        Index(
            'idx_solution_task_user',
            'challenge_id', 'user_id'
        ),
    )
