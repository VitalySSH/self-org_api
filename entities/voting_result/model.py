from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base

if TYPE_CHECKING:
    from datastorage.database.models import VotingOption


class VotingResult(Base):
    __tablename__ = TableName.VOTING_RESULT

    only_option_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.VOTING_OPTION}.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    only_option: Mapped['VotingOption'] = relationship(lazy='noload')
    multiple_options: Mapped[List['VotingOption']] = relationship(
        secondary=TableName.RELATION_VR_VO, lazy='noload')
    member_id: Mapped[str] = mapped_column(nullable=False, index=True)
    initiative_id: Mapped[str] = mapped_column(nullable=True, index=True)
