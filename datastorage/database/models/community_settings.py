from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import (
        InitiativeCategory, Community, User, DelegateSettings
    )


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    user: Mapped['User'] = relationship(lazy='noload')
    community_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY}.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    community: Mapped['Community'] = relationship(
        foreign_keys=f'{TableName.COMMUNITY_SETTINGS}.c.community_id', lazy='noload')
    name: Mapped[str] = mapped_column(nullable=False)
    quorum: Mapped[int] = mapped_column(nullable=False)
    vote: Mapped[int] = mapped_column(nullable=False)
    init_categories: Mapped[List['InitiativeCategory']] = relationship(
        secondary=TableName.RELATION_CS_CATEGORIES, lazy='noload')
    delegate_settings: Mapped[List['DelegateSettings']] = relationship(
        secondary=TableName.RELATION_CS_DS, lazy='noload')
