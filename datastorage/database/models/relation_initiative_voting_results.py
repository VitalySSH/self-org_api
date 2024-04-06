from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationInitiativeRV(Base):
    __tablename__ = TableName.RELATION_INITIATIVE_RV
    __table_args__ = (
        UniqueConstraint(
            'initiative_id', 'result_voting_id', name='idx_unique_initiative_result_voting'),
    )

    initiative_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE}.id', ondelete='CASCADE'),
        nullable=False, index=True)
    result_voting_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.RESULT_VOTING}.id', ondelete='CASCADE'),
        nullable=False, index=True)
