from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class RelationChallengeSolutions(Base):
    __tablename__ = TableName.RELATION_CHALLENGE_SOLUTIONS
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_challenge_solutions'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CHALLENGE}.id', ondelete="CASCADE"),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.SOLUTION}.id', ondelete="CASCADE"),
        nullable=False, index=True)
