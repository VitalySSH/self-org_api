from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import (
        CommunitySettings, User
    )


class Community(Base):
    __tablename__ = TableName.COMMUNITY

    main_settings_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    main_settings: Mapped['CommunitySettings'] = relationship(
        lazy='noload',
        foreign_keys=f'{TableName.COMMUNITY}.c.main_settings_id'
    )
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    created: Mapped[datetime] = mapped_column(default=datetime.now)
