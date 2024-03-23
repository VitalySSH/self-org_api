from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, User, JOIN_DEPTH

if TYPE_CHECKING:
    from datastorage.database.models import InitiativeCategory


class CommunitySettings(Base):
    __tablename__ = TableName.COMMUNITY_SETTINGS

    user: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=True, index=True
    )
    user_rel: Mapped[User] = relationship(join_depth=JOIN_DEPTH, lazy=False)
    community: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY}.id'),
        nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    quorum: Mapped[int] = mapped_column(nullable=False)
    vote: Mapped[int] = mapped_column(nullable=False)
    init_categories_rel: Mapped[List['InitiativeCategory']] = relationship(
        secondary=TableName.CS_CATEGORIES,
        join_depth=JOIN_DEPTH,
        lazy=False,
    )
