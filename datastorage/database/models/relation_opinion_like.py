from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationOpinionLike(Base):
    __tablename__ = TableName.RELATION_OPINION_LIKE
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_opinion_like'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.OPINION}.id'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.LIKE}.id'),
        nullable=False, index=True)
