from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid


class RelationDsUsers(Base):
    __tablename__ = TableName.RELATION_DS_USERS
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_delegate_settings_users'),
    )
    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.DELEGATE_SETTINGS}.id'),
        nullable=False, index=True)

    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id'),
        nullable=False, index=True)
