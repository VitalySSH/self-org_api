from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import VotingOption


class VotingResult(Base):
    __tablename__ = TableName.VOTING_RESULT

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    vote: Mapped[bool] = mapped_column(nullable=True)
    is_significant_minority: Mapped[bool] = mapped_column(
        nullable=False, default=False)
    selected_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_VR_VO, lazy='noload')
