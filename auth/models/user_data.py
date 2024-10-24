from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import User


class UserData(Base):
    __tablename__ = TableName.USER_DATA

    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    user: Mapped['User'] = relationship(lazy='noload', uselist=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
