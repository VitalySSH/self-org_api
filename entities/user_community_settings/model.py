from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import (
        Category, User, DelegateSettings, CommunityName, CommunityDescription,
        RequestMember
    )


class UserCommunitySettings(Base):
    __tablename__ = TableName.USER_COMMUNITY_SETTINGS
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'community_id', name='idx_unique_user_cs_community_user'),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True,
        index=True,
    )
    user: Mapped['User'] = relationship(lazy='noload')
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    parent_community_id: Mapped[str] = mapped_column(nullable=True, index=True)
    name_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_NAME}.id'),
        nullable=False,
        index=True,
    )
    name: Mapped['CommunityName'] = relationship(lazy='noload')
    description_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_DESCRIPTION}.id'),
        nullable=False,
        index=True,
    )
    description: Mapped['CommunityDescription'] = relationship(lazy='noload')
    quorum: Mapped[int] = mapped_column(nullable=False, index=True)
    vote: Mapped[int] = mapped_column(nullable=False, index=True)
    significant_minority: Mapped[int] = mapped_column(nullable=False, index=True)
    is_secret_ballot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_minority_not_participate: Mapped[bool] = mapped_column(nullable=False, default=False)
    categories: Mapped[List['Category']] = relationship(
        secondary=TableName.RELATION_UCS_CATEGORIES, lazy='noload'
    )
    sub_communities_settings: Mapped[List['UserCommunitySettings']] = relationship(
        secondary=TableName.RELATION_UCS_UCS,
        primaryjoin='UserCommunitySettings.id == RelationUserCsUserCs.from_id',
        secondaryjoin='UserCommunitySettings.id == RelationUserCsUserCs.to_id',
        lazy='noload'
    )
    delegate_settings: Mapped[List['DelegateSettings']] = relationship(
        secondary=TableName.RELATION_UCS_DS, lazy='noload')
    is_not_delegate: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_default_add_member: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
    adding_members: Mapped[List['RequestMember']] = relationship(
        secondary=TableName.RELATION_UCS_REQUEST_MEMBER,
        lazy='noload',
        cascade='all,delete',
        passive_deletes=True,
    )
