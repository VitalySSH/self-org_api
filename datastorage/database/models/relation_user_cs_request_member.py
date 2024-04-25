from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationUserCsRequestMember(Base):
    __tablename__ = TableName.RELATION_UCS_REQUEST_MEMBER
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_user_community_settings_request_member'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id'), nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.REQUEST_MEMBER}.id'), nullable=False, index=True)
