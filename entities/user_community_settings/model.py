from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import (
        InitiativeCategory, User, DelegateSettings
    )


class UserCommunitySettings(Base):
    __tablename__ = TableName.USER_COMMUNITY_SETTINGS

    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    user: Mapped['User'] = relationship(lazy='noload')
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    quorum: Mapped[int] = mapped_column(nullable=False)
    vote: Mapped[int] = mapped_column(nullable=False)
    is_secret_ballot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    init_categories: Mapped[List['InitiativeCategory']] = relationship(
        secondary=TableName.RELATION_UCS_CATEGORIES, lazy='noload')
    delegate_settings: Mapped[List['DelegateSettings']] = relationship(
        secondary=TableName.RELATION_UCS_DS, lazy='noload')
    is_not_delegate: Mapped[bool] = mapped_column(nullable=False, default=False)
