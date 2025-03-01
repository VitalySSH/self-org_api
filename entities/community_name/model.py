from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class CommunityName(Base):
    __tablename__ = TableName.COMMUNITY_NAME
    __table_args__ = (
        UniqueConstraint(
            'name', 'community_id', name='idx_unique_community_name_id'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    name: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    is_readonly: Mapped[bool] = mapped_column(default=False)
