from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class Solution(Base):
    __tablename__ = TableName.SOLUTION

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    text: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
