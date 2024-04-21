from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class CommunityName(Base):
    __tablename__ = TableName.COMMUNITY_NAME
    __table_args__ = (
        UniqueConstraint(
            'name', 'community_id', name='idx_unique_community_name_id'),
    )

    name: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)

