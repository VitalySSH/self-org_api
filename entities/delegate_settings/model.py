from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import Category, User


class DelegateSettings(Base):
    __tablename__ = TableName.DELEGATE_SETTINGS

    category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CATEGORY}.id'),
        nullable=False,
        index=True,
    )
    category: Mapped['Category'] = relationship(lazy='noload')
    user_id: Mapped[str] = mapped_column(nullable=False, index=True)
    delegates: Mapped[List['User']] = relationship(
        secondary=TableName.RELATION_DS_USERS, lazy='noload')
