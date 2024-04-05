from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, Status, InitiativeCategory, User


class Initiative(Base):
    __tablename__ = TableName.INITIATIVE

    content: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    creator: Mapped[User] = relationship(lazy='noload')
    status_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.STATUS}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    status: Mapped[Status] = relationship(lazy='noload')
    category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    category: Mapped[InitiativeCategory] = relationship(lazy='noload')
