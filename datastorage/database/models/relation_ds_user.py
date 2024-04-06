from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationDSUsers(Base):
    __tablename__ = TableName.RELATION_DS_USERS
    __table_args__ = (
        UniqueConstraint('ds_id', 'user_id', name='idx_unique_ds_user'),
    )

    ds_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.DELEGATE_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)

    user_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER}.id', ondelete='CASCADE'),
        nullable=False, index=True)
