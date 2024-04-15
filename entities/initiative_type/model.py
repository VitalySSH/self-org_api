from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class InitiativeType(Base):
    __tablename__ = TableName.INITIATIVE_TYPE

    code: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
