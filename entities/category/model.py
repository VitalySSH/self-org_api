from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import Status


class Category(Base):
    __tablename__ = TableName.CATEGORY

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    name: Mapped[str] = mapped_column(nullable=False)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    status_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id'),
        nullable=False,
        index=True,
    )
    status: Mapped['Status'] = relationship(lazy='noload')
