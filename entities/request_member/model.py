from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import User, Community, Status


class RequestMember(Base):
    __tablename__ = TableName.REQUEST_MEMBER
    __table_args__ = (
        UniqueConstraint(
            'member_id', 'community_id', 'parent_id',
            name='idx_unique_request_member'
        ),
    )

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    member_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True,
        index=True,
    )
    member: Mapped['User'] = relationship(
        lazy='noload',
        foreign_keys=f'{TableName.REQUEST_MEMBER}.c.member_id',
    )
    community_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY}.id'),
        nullable=True,
        index=True,
    )
    community: Mapped['Community'] = relationship(lazy='noload')
    status_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id'),
        nullable=False,
        index=True,
    )
    status: Mapped['Status'] = relationship(lazy='noload')
    vote: Mapped[bool] = mapped_column(nullable=True)
    reason: Mapped[str] = mapped_column(nullable=True)
    parent_id: Mapped[str] = mapped_column(nullable=True)
    created: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now
    )
    updated: Mapped[datetime] = mapped_column(nullable=True)
