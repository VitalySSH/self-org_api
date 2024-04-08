from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import User, Initiative, Like


class Opinion(Base):
    __tablename__ = TableName.OPINION

    EXCLUDE_READ_FIELDS = ['likes']

    text: Mapped[str] = mapped_column(nullable=False)
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
    likes: Mapped[List['Like']] = relationship(
        secondary=TableName.RELATION_OPINION_LIKE, lazy='noload')
