from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import(
        InteractionCombination, Solution
    )


class CombinationSourceElement(Base):
    __tablename__ = TableName.COMBINATION_SOURCE_ELEMENT

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    combination_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INTERACTION_COMBINATION}.id'),
        nullable=False,
        index=True
    )
    source_solution_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.SOLUTION}.id'),
        nullable=False,
        index=True
    )
    element_description: Mapped[str] = mapped_column(nullable=False)
    element_context: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    combination: Mapped['InteractionCombination'] = (
        relationship(lazy='noload')
    )
    source_solution: Mapped['Solution'] = relationship(lazy='noload')

    __table_args__ = (
        Index(
            'idx_combination_source',
            'combination_id',
            'source_solution_id'
        ),
    )
