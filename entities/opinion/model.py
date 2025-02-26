from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base, User
from datastorage.utils import build_uuid


class Opinion(Base):
    __tablename__ = TableName.OPINION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    text: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False,
        index=True,
    )
    creator: Mapped['User'] = relationship(lazy='noload')
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
    rule_id: Mapped[str] = mapped_column(nullable=True, index=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
