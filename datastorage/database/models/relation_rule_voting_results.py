from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationRuleVotingResult(Base):
    __tablename__ = TableName.RELATION_RULE_VR
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_rule_voting_results'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.RULE}.id'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_RESULT}.id'),
        nullable=False, index=True)
