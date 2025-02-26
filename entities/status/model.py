from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class Status(Base):
    __tablename__ = TableName.STATUS

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    code: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
