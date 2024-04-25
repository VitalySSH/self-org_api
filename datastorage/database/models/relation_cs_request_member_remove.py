from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationCsRequestMemberRemove(Base):
    __tablename__ = TableName.RELATION_CS_REQUEST_MEMBER_REMOVE
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_community_settings_request_member_remove'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id'), nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.REQUEST_MEMBER}.id'), nullable=False, index=True)
