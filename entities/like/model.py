from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class Like(Base):
    __tablename__ = TableName.LIKE

    is_like: Mapped[bool] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
    opinion_id: Mapped[str] = mapped_column(nullable=True, index=True)
