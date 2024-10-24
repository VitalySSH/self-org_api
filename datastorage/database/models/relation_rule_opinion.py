from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationRuleOpinion(Base):
    __tablename__ = TableName.RELATION_RULE_OPINION
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_rule_opinion'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.RULE}.id', ondelete="CASCADE"),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.OPINION}.id', ondelete="CASCADE"),
        nullable=False, index=True)
