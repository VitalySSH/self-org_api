from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import RequestMember


class User(Base):
    __tablename__ = TableName.USER

    EXCLUDE_READ_FIELDS = ['hashed_password']

    firstname: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    about_me: Mapped[str] = mapped_column(nullable=True)
    foto_id: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    adding_communities: Mapped[List['RequestMember']] = relationship(
        secondary=TableName.RELATION_USER_REQUEST_MEMBER, lazy='noload')
