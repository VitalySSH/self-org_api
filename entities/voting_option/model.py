from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class VotingOption(Base):
    __tablename__ = TableName.VOTING_OPTION

    content: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[str] = mapped_column(nullable=False, index=True)
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
