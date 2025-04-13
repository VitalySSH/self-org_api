from typing import Dict

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid
from entities.noncompliance.crud.dataclasses import NoncomplianceData
from entities.voting_option.dataclasses import VotingOptionData


class VotingResult(Base):
    __tablename__ = TableName.VOTING_RESULT

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    vote: Mapped[bool] = mapped_column(nullable=True)
    is_significant_minority: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    is_noncompliance_minority: Mapped[bool] = mapped_column(
        nullable=False, default=False
    )
    options: Mapped[Dict[str, VotingOptionData]] = mapped_column(
        JSON, default=dict
    )
    minority_options: Mapped[Dict[str, VotingOptionData]] = mapped_column(
        JSON, default=dict
    )
    noncompliance: Mapped[Dict[str, NoncomplianceData]] = mapped_column(
        JSON, default=dict
    )
    minority_noncompliance: Mapped[Dict[str, NoncomplianceData]] = (
        mapped_column(JSON, default=dict)
    )
