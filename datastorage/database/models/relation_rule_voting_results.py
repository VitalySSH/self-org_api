from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationRuleUserVR(Base):
    __tablename__ = TableName.RELATION_RULE_USER_VR
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_rule_user_voting_results'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.RULE}.id'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_VOTING_RESULT}.id'),
        nullable=False, index=True)
