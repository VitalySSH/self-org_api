from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import (
        InitiativeCategory, CommunityName, CommunityDescription
    )


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

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
    quorum: Mapped[int] = mapped_column(nullable=False)
    vote: Mapped[int] = mapped_column(nullable=False)
    #  TODO для данных полей, функционал будет реализован позже
    is_secret_ballot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_minority_not_participate: Mapped[bool] = mapped_column(nullable=False, default=True)
    #
    init_categories: Mapped[List['InitiativeCategory']] = relationship(
        secondary=TableName.RELATION_CS_CATEGORIES, lazy='noload')
