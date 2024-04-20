from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class FileMetaData(Base):
    __tablename__ = TableName.FILE_METADATA

    name: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False)
    mimetype: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    updated: Mapped[datetime] = mapped_column(nullable=True)
