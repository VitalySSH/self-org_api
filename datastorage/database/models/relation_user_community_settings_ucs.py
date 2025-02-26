from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class RelationUserCsUserCs(Base):
    __tablename__ = TableName.RELATION_UCS_UCS
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_user_community_settings_user_cs'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id'),
        primary_key=True
    )
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id'),
        primary_key=True
    )
