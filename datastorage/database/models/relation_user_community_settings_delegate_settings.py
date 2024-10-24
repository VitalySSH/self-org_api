from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationUCsDs(Base):
    __tablename__ = TableName.RELATION_UCS_DS
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_user_community_settings_delegate_settings'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id', ondelete="CASCADE"),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.DELEGATE_SETTINGS}.id', ondelete="CASCADE"),
        nullable=False, index=True)
