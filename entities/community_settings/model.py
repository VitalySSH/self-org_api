from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid
from entities.community_settings.crud.schemas import LastVotingParams

if TYPE_CHECKING:
    from datastorage.database.models import (
        Category, CommunityName, CommunityDescription, RequestMember,
        UserCommunitySettings
    )


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    name_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_NAME}.id'),
        nullable=True,
        index=True,
    )
    name: Mapped['CommunityName'] = relationship(lazy='noload')
    description_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_DESCRIPTION}.id'),
        nullable=True,
        index=True,
    )
    description: Mapped['CommunityDescription'] = relationship(lazy='noload')
    quorum: Mapped[int] = mapped_column(nullable=True)
    vote: Mapped[int] = mapped_column(nullable=True)
    significant_minority: Mapped[int] = mapped_column(nullable=True)
    last_voting_params: Mapped[LastVotingParams] = mapped_column(
        JSON, nullable=True
    )
    #  TODO: для данных полей, функционал будет реализован позже
    is_secret_ballot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_minority_not_participate: Mapped[bool] = mapped_column(nullable=False, default=True)
    #
    categories: Mapped[List['Category']] = relationship(
        secondary=TableName.RELATION_CS_CATEGORIES, lazy='noload')
    sub_communities_settings: Mapped[List['UserCommunitySettings']] = relationship(
        secondary=TableName.RELATION_CS_UCS, lazy='noload')
    adding_members: Mapped[List['RequestMember']] = relationship(
        secondary=TableName.RELATION_CS_REQUEST_MEMBER, lazy='noload')
