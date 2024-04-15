from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datastorage.database.classes import TableName
from datastorage.database.models import Base


class RelationUserCsCategories(Base):
    __tablename__ = TableName.RELATION_UCS_CATEGORIES
    __table_args__ = (
        UniqueConstraint(
            'from_id', 'to_id', name='idx_unique_user_community_settings_init_categories'),
    )

    from_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.USER_COMMUNITY_SETTINGS}.id', ondelete='CASCADE'),
        nullable=False, index=True)
    to_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id', ondelete='CASCADE'),
        nullable=False, index=True)
