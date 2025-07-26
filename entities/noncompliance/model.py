from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class Noncompliance(Base):
    """Последствия несоблюдения правил."""
    __tablename__ = TableName.NONCOMPLIANCE

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    name: Mapped[str] = mapped_column(nullable=False)
    community_id: Mapped[str] = mapped_column(nullable=False, index=True)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
