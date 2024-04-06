from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationCsDs(Base):
    __tablename__ = TableName.RELATION_CS_DS
    __table_args__ = (
        UniqueConstraint('cs_id', 'ds_id', name='idx_unique_cs_ds'),
    )

    cs_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)
    ds_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.DELEGATE_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)
