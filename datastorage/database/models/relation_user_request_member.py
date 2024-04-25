from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationUserRequestMember(Base):
    __tablename__ = TableName.RELATION_USER_REQUEST_MEMBER
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_user_request_member'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'), nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.REQUEST_MEMBER}.id'), nullable=False, index=True)
