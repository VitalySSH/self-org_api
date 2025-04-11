from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, event, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        CommunitySettings, User, UserCommunitySettings
    )


class Community(Base):
    __tablename__ = TableName.COMMUNITY

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    main_settings_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id'),
        nullable=False,
        index=True,
    )
    main_settings: Mapped['CommunitySettings'] = relationship(
        lazy='noload',
        foreign_keys=f'{TableName.COMMUNITY}.c.main_settings_id'
    )
    user_settings: Mapped[List['UserCommunitySettings']] = relationship(
        secondary=TableName.RELATION_COMMUNITY_UCS, lazy='noload')
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    parent_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY}.id'),
        nullable=True,
        index=True,
    )
    parent: Mapped['Community'] = relationship(lazy='noload', remote_side=[id])
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    tracker: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)


@event.listens_for(Community, 'before_insert')
def before_insert_listener(mapper, connection, target):
    if target.parent is not None and target.tracker is None:
        count = connection.scalar(
            select(func.count(Community.id))
            .where(Community.parent_id == target.parent.id)
        )
        target.tracker = f'ПС-{count + 1}'
