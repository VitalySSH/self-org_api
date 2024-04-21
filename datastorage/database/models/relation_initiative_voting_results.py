from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationInitiativeRV(Base):
    __tablename__ = TableName.RELATION_INITIATIVE_VR
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_initiative_result_voting'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE}.id'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False, index=True)
