from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base


if TYPE_CHECKING:
    from datastorage.database.models import InitiativeCategory, User


class DelegateSettings(Base):
    __tablename__ = TableName.DELEGATE_SETTINGS

    init_category_id: Mapped[str] = mapped_column(
        ForeignKey(f'{TableName.INITIATIVE_CATEGORY}.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    init_category: Mapped['InitiativeCategory'] = relationship(lazy='noload')
    voting_results: Mapped[List['User']] = relationship(
        secondary=TableName.RELATION_DS_USERS, lazy='noload')
