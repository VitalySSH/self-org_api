from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import CollectiveInteraction


class InteractionSuggestion(Base):
    __tablename__ = TableName.INTERACTION_SUGGESTION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    interaction_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COLLECTIVE_INTERACTION}.id'),
        nullable=False,
        index=True
    )
    element_description: Mapped[str] = mapped_column(nullable=False)
    integration_advice: Mapped[str] = mapped_column(nullable=False)
    source_solutions_count: Mapped[int] = mapped_column(nullable=False)
    reasoning: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    interaction: Mapped['CollectiveInteraction'] = relationship(
        back_populates='suggestions',
        lazy='noload'
    )
