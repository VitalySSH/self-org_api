from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datastorage.utils import build_uuid


JOIN_DEPTH = 5


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
