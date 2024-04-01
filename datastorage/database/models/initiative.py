from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, Status, InitiativeCategory, JOIN_DEPTH, User


class Initiative(Base):
    __tablename__ = TableName.INITIATIVE

    content: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped[User] = relationship(join_depth=JOIN_DEPTH, lazy=False)
    status_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id'),
        nullable=False,
        index=True,
    )
    status: Mapped[Status] = relationship(join_depth=JOIN_DEPTH, lazy=False)
    category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id'),
        nullable=False,
        index=True,
    )
    category: Mapped[InitiativeCategory] = relationship(join_depth=JOIN_DEPTH, lazy=False)
