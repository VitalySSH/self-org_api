from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import User


class ResultVoting(Base):
    __tablename__ = TableName.RESULT_VOTING

    vote: Mapped[int] = mapped_column(nullable=False)
    member_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    member: Mapped['User'] = relationship(lazy='noload')
