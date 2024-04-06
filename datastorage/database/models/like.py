from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import User, Initiative, Opinion


class Like(Base):
    __tablename__ = TableName.LIKE

    is_like: Mapped[bool] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    initiative_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    initiative: Mapped['Initiative'] = relationship(lazy='noload')
    opinion_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.OPINION}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    opinion: Mapped['Opinion'] = relationship(lazy='noload')
