from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import Category, User


class DelegateSettings(Base):
    __tablename__ = TableName.DELEGATE_SETTINGS

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.CATEGORY}.id'),
        nullable=False,
        index=True,
    )
    category: Mapped['Category'] = relationship(lazy='noload')
    user_id: Mapped[str] = mapped_column(nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    delegate_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    delegate: Mapped['User'] = relationship(lazy='noload')
