from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationCsCategories(Base):
    __tablename__ = TableName.RELATION_CS_CATEGORIES
    __table_args__ = (
        UniqueConstraint('from_id', 'to_id', name='idx_unique_cs_init_category'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.COMMUNITY_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id', ondelete='CASCADE'),
        nullable=False, index=True)
