from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, Status, JOIN_DEPTH


class InitiativeCategory(Base):
    __tablename__ = TableName.INITIATIVE_CATEGORY

    name: Mapped[str] = mapped_column(nullable=False)
    creator: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id'),
        nullable=False,
        index=True,
    )
    status_rel: Mapped[Status] = relationship(
        join_depth=JOIN_DEPTH,
        lazy=False,
        foreign_keys=f'{TableName.INITIATIVE_CATEGORY}.c.status'
    )
