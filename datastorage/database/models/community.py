from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, CommunitySettings, User, JOIN_DEPTH


class Community(Base):
    __tablename__ = TableName.COMMUNITY

    main_settings_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id'),
        nullable=False, index=True
    )
    main_settings: Mapped[CommunitySettings] = relationship(
        join_depth=JOIN_DEPTH,
        lazy=False,
        foreign_keys=f'{TableName.COMMUNITY}.c.main_settings_id'
    )
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped[User] = relationship(join_depth=JOIN_DEPTH, lazy=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
