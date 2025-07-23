from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class RelationUserCsResponsibilities(Base):
    __tablename__ = TableName.RELATION_UCS_RESPONSIBILITIES
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id',
            name='idx_unique_user_cs_responsibility'
        ),
    )

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.RESPONSIBILITY}.id', ondelete='CASCADE'),
        nullable=False, index=True)
