from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import VotingOption


class VotingResult(Base):
    __tablename__ = TableName.VOTING_RESULT

    vote: Mapped[bool] = mapped_column(nullable=True)
    extra_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_VR_VO, lazy='noload')
    member_id: Mapped[str] = mapped_column(nullable=False, index=True)
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
