from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        VersionInteractionInfluence, Solution
    )


class SolutionVersion(Base):
    __tablename__ = TableName.SOLUTION_VERSION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    solution_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.SOLUTION}.id'),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(nullable=False)
    change_description: Mapped[str] = mapped_column(nullable=False)
    version_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    solution: Mapped['Solution'] = relationship(
        back_populates='versions',
        lazy='noload'
    )
    influences: Mapped[List['VersionInteractionInfluence']] = relationship(
        back_populates='solution_version',
        lazy='noload'
    )

    __table_args__ = (
        UniqueConstraint(
            'solution_id', 'version_number',
            name='uq_solution_version_number'
        ),
        Index(
            'idx_version_solution_number',
            'solution_id', 'version_number'
        ),
    )
