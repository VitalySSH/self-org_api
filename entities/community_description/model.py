from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class CommunityDescription(Base):
    __tablename__ = TableName.COMMUNITY_DESCRIPTION
    __table_args__ = (
        UniqueConstraint(
            'value', 'community_id', name='idx_unique_community_description_id'),
    )

    value: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False)
    is_readonly: Mapped[bool] = mapped_column(nullable=False, default=False)
