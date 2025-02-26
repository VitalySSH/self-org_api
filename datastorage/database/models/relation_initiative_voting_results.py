from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class RelationInitiativeUserVR(Base):
    __tablename__ = TableName.RELATION_INITIATIVE_USER_VR
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_initiative_user_voting_results'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE}.id'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_VOTING_RESULT}.id'),
        nullable=False, index=True)
