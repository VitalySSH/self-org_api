from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class CommunityDescription(Base):
    __tablename__ = TableName.COMMUNITY_DESCRIPTION
    __table_args__ = (
        UniqueConstraint(
            'value', 'community_id', name='idx_unique_community_description_id'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    value: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False)
    is_readonly: Mapped[bool] = mapped_column(default=False)
