from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import Initiative, Opinion


class Like(Base):
    __tablename__ = TableName.LIKE

    is_like: Mapped[bool] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
    opinion_id: Mapped[str] = mapped_column(nullable=True, index=True)
    initiatives_set: Mapped[List['Initiative']] = relationship(
        back_populates='likes', lazy='noload')
    opinions_set: Mapped[List['Opinion']] = relationship(
        back_populates='likes', lazy='noload')
