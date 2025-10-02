from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid
from entities.collective_interaction.crud.enums import (
    UserResponse
)

if TYPE_CHECKING:
    from datastorage.database.models import (
        Solution, InteractionSuggestion, InteractionCriticism,
        InteractionCombination, VersionInteractionInfluence
    )


class CollectiveInteraction(Base):
    __tablename__ = TableName.COLLECTIVE_INTERACTION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    solution_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.SOLUTION}.id'),
        nullable=False,
        index=True
    )
    interaction_type: Mapped[str] = mapped_column(nullable=False)
    user_response: Mapped[str] = mapped_column(
        nullable=False,
        default=UserResponse.PENDING.value,
    )
    user_reasoning: Mapped[Optional[str]] = mapped_column(nullable=True)
    applied_to_solution: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    responded_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    solution: Mapped['Solution'] = relationship(
        back_populates='interactions',
        lazy='noload'
    )
    suggestions: Mapped[List['InteractionSuggestion']] = relationship(
        back_populates='interaction',
        lazy='noload'
    )
    criticisms: Mapped[List['InteractionCriticism']] = relationship(
        back_populates='interaction',
        lazy='noload'
    )
    combinations: Mapped[List['InteractionCombination']] = relationship(
        back_populates='interaction',
        lazy='noload'
    )
    influences: Mapped[List['VersionInteractionInfluence']] = relationship(
        back_populates='collective_interaction',
        lazy='noload'
    )

    __table_args__ = (
        Index(
            'idx_interaction_solution_created',
            'solution_id', 'created_at'
        ),
        Index('idx_interaction_type_response',
              'interaction_type', 'user_response'
              ),
    )
