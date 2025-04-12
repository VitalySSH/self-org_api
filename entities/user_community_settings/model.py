from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import (
        Category, User, CommunityName, CommunityDescription, Responsibility,
        Community
    )


class UserCommunitySettings(Base):
    __tablename__ = TableName.USER_COMMUNITY_SETTINGS
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'community_id', name='idx_unique_user_cs_community_user'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True,
        index=True,
    )
    user: Mapped['User'] = relationship(lazy='noload')
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    parent_community_id: Mapped[str] = mapped_column(nullable=True, index=True)
    community: Mapped['Community'] = relationship(
        foreign_keys=[community_id],
        primaryjoin='UserCommunitySettings.community_id == Community.id',
        lazy='noload',
        back_populates='user_settings',
        # innerjoin=True,
        viewonly=True,
    )
    names: Mapped[List['CommunityName']] = relationship(
        secondary=TableName.RELATION_UCS_NAMES,
        lazy='noload'
    )

    descriptions: Mapped[List['CommunityDescription']] = relationship(
        secondary=TableName.RELATION_UCS_DESCRIPTIONS,
        lazy='noload'
    )
    quorum: Mapped[int] = mapped_column(nullable=False, index=True)
    vote: Mapped[int] = mapped_column(nullable=False, index=True)
    significant_minority: Mapped[int] = mapped_column(
        nullable=False, index=True
    )
    decision_delay: Mapped[int] = mapped_column(nullable=True)
    dispute_time_limit: Mapped[int] = mapped_column(nullable=True)
    is_secret_ballot: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_minority_not_participate: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    categories: Mapped[List['Category']] = relationship(
        secondary=TableName.RELATION_UCS_CATEGORIES, lazy='noload'
    )
    sub_communities_settings: Mapped[List['UserCommunitySettings']] = (
        relationship(
            secondary=TableName.RELATION_UCS_UCS,
            primaryjoin=('UserCommunitySettings.id == '
                         'RelationUserCsUserCs.from_id'),
            secondaryjoin=('UserCommunitySettings.id == '
                           'RelationUserCsUserCs.to_id'),
            lazy='noload'
        )
    )
    responsibilities: Mapped[List['Responsibility']] = relationship(
        secondary=TableName.RELATION_UCS_RESPONSIBILITIES, lazy='noload'
    )
    is_not_delegate: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    is_default_add_member: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
