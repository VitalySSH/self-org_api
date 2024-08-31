from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationCommunityUCs(Base):
    __tablename__ = TableName.RELATION_COMMUNITY_UCS
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_community_user_community_settings'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY}.id', ondelete="CASCADE"),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id', ondelete="CASCADE"),
        nullable=False, index=True)
