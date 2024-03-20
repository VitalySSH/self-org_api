from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationCSCategories(Base):
    __tablename__ = TableName.CS_CATEGORIES
    __table_args__ = (
        UniqueConstraint('cs_id', 'init_category_id', name='idx_unique_cs_init_category'),
    )

    cs_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id'),
        nullable=False, index=True)
    init_category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id'),
        nullable=False, index=True)
