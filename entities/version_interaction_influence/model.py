from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        SolutionVersion, CollectiveInteraction
    )


class VersionInteractionInfluence(Base):
    __tablename__ = TableName.VERSION_INTERACTION_INFLUENCE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    solution_version_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.SOLUTION_VERSION}.id'),
        nullable=False,
        index=True
    )
    collective_interaction_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COLLECTIVE_INTERACTION}.id'),
        nullable=False,
        index=True
    )
    influence_type: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    solution_version: Mapped['SolutionVersion'] = relationship(
        back_populates='influences',
        lazy='noload'
    )
    collective_interaction: Mapped['CollectiveInteraction'] = relationship(
        back_populates='influences',
        lazy='noload'
    )

    __table_args__ = (
        UniqueConstraint(
            'solution_version_id',
            'collective_interaction_id',
            name='uq_version_interaction_influence'
        ),
    )
