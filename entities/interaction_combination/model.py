from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        CollectiveInteraction, CombinationSourceElement
    )

class InteractionCombination(Base):
    __tablename__ = TableName.INTERACTION_COMBINATION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    interaction_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COLLECTIVE_INTERACTION}.id'),
        nullable=False,
        index=True
    )
    new_idea_description: Mapped[str] = mapped_column(nullable=False)
    potential_impact: Mapped[str] = mapped_column(nullable=False)
    reasoning: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    interaction: Mapped['CollectiveInteraction'] = relationship(
        back_populates='combinations',
        lazy='noload'
    )
    source_elements: Mapped[List['CombinationSourceElement']] = relationship(
        back_populates='combination',
        lazy='noload'
    )
