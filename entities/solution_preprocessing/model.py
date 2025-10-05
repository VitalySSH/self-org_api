from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datastorage.database.classes import TableName
from datastorage.database.models import Base
from datastorage.utils import build_uuid

if TYPE_CHECKING:
    from datastorage.database.models import Solution


class SolutionPreprocessing(Base):
    """
    Предобработанные данные решения для оптимизации анализа

    Хранит:
    - Embedding (JSON) для semantic search
    - Ключевые тезисы
    - Категорию/тему
    - Метрики качества
    - Кластер (если применимо)
    """
    __tablename__ = TableName.SOLUTION_PREPROCESSING

    id: Mapped[str] = mapped_column(primary_key=True, default=build_uuid)
    solution_id: Mapped[str] = mapped_column(
        ForeignKey('solution.id'),
        nullable=False,
        unique=True,
        index=True
    )

    # Embedding для semantic search (храним как JSON, т.к. нет pgvector)
    # В будущем можно мигрировать на pgvector
    embedding: Mapped[str] = mapped_column(nullable=False)  # JSON array

    # Извлеченные ключевые тезисы (2-3 предложения)
    key_points: Mapped[str] = mapped_column(nullable=False)

    # Категория решения (технический/социальный/креативный и т.д.)
    category: Mapped[str] = mapped_column(nullable=False, index=True)

    # Метрики качества (JSON)
    metrics: Mapped[str] = mapped_column(nullable=False)  # JSON object

    # ID кластера (заполняется при batch кластеризации)
    cluster_id: Mapped[Optional[int]] = mapped_column(
        nullable=True, index=True
    )

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now
    )

    # Relationships
    solution: Mapped['Solution'] = relationship(lazy='noload')

    __table_args__ = (
        Index('idx_preprocessing_category_cluster',
              'category', 'cluster_id'),
    )
