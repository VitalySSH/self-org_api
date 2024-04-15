from typing import List, TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import InitiativeCategory


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    name: Mapped[str] = mapped_column(nullable=False)
    quorum: Mapped[int] = mapped_column(nullable=False)
    vote: Mapped[int] = mapped_column(nullable=False)
    # TODO для данных полей, функционал будет реализован позже
    is_secret_ballot: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_can_offer: Mapped[bool] = mapped_column(nullable=False, default=False)
    #
    init_categories: Mapped[List['InitiativeCategory']] = relationship(
        secondary=TableName.RELATION_CS_CATEGORIES, lazy='noload')
