from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationInitiativeOpinion(Base):
    __tablename__ = TableName.RELATION_INITIATIVE_OPINION
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_initiative_opinion'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE}.id', ondelete="CASCADE"),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.OPINION}.id', ondelete="CASCADE"),
        nullable=False, index=True)
