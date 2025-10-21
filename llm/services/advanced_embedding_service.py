"""
Advanced Embedding Service с использованием Sentence Transformers

Для активации:
1. Установите: pip install sentence-transformers
2. В preprocessing_service.py замените:
   self._generate_improved_embedding() → self._generate_transformer_embedding()

Модель all-MiniLM-L6-v2:
- Размер: ~80MB
- Размерность: 384
- Качество: отличное для семантического поиска
- Скорость: ~100 предложений/сек на CPU
"""

import json
from typing import List, Optional
import numpy as np

# Импорт будет работать только если установлен sentence-transformers
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class AdvancedEmbeddingService:
    """
    Сервис для генерации высококачественных embeddings

    Использует предобученные модели sentence-transformers
    для максимального качества семантического поиска
    """

    def __init__(
            self,
            model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder: Optional[str] = None
    ):
        """
        Args:
            model_name: Название модели из HuggingFace
            cache_folder: Папка для кеширования модели (опционально)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers не установлен. "
                "Установите: pip install sentence-transformers"
            )

        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self.cache_folder = cache_folder
        self.embedding_dim = 384  # Для all-MiniLM-L6-v2

    @property
    def model(self) -> SentenceTransformer:
        """Lazy loading модели"""
        if self._model is None:
            print(f"🔄 Загружаю модель {self.model_name}...")
            self._model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_folder
            )
            print("✅ Модель загружена")
        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        """
        Генерация высококачественного embedding

        Args:
            text: Текст для векторизации

        Returns:
            Нормализованный вектор размерности 384
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dim

        # Генерируем embedding
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,  # Автоматическая нормализация
            show_progress_bar=False
        )

        return embedding.tolist()

    def generate_embeddings_batch(
            self,
            texts: List[str],
            batch_size: int = 32
    ) -> List[List[float]]:
        """
        Пакетная генерация embeddings (эффективнее для больших объёмов)

        Args:
            texts: Список текстов
            batch_size: Размер батча

        Returns:
            Список векторов
        """
        if not texts:
            return []

        # Фильтруем пустые тексты
        valid_texts = [t if t and t.strip() else " " for t in texts]

        # Генерируем батчем
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 100
        )

        return [emb.tolist() for emb in embeddings]

    def compute_similarity(
            self,
            embedding1: List[float],
            embedding2: List[float]
    ) -> float:
        """
        Вычисление cosine similarity между embedding

        Так как embeddings нормализованы, это просто dot product
        """
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)
        return float(np.dot(arr1, arr2))

    def find_most_similar(
            self,
            query_embedding: List[float],
            candidate_embeddings: List[List[float]],
            top_k: int = 10
    ) -> List[tuple]:
        """
        Поиск наиболее похожих embeddings

        Args:
            query_embedding: Embedding запроса
            candidate_embeddings: Список кандидатов
            top_k: Сколько вернуть

        Returns:
            List[(index, similarity_score)]
        """
        query = np.array(query_embedding)
        candidates = np.array(candidate_embeddings)

        # Косинусное сходство = dot product (так как нормализовано)
        similarities = np.dot(candidates, query)

        # Топ-K индексов
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [
            (int(idx), float(similarities[idx]))
            for idx in top_indices
        ]


class HybridEmbeddingService:
    """
    Гибридный сервис: комбинирует transformer embeddings с легковесными

    Стратегия:
    - Для предобработки (preprocessing) используем transformer
    - Для быстрого поиска используем кешированные embeddings
    - Fallback на легковесные если transformer недоступен
    """

    def __init__(
            self,
            use_transformers: bool = True,
            fallback_service=None
    ):
        """
        Args:
            use_transformers: Использовать ли transformer модель
            fallback_service: Сервис для fallback (из improved_preprocessing)
        """
        self.use_transformers = use_transformers and SENTENCE_TRANSFORMERS_AVAILABLE
        self.fallback_service = fallback_service

        if self.use_transformers:
            self.transformer_service = AdvancedEmbeddingService()
        else:
            self.transformer_service = None

    def generate_embedding(self, text: str) -> List[float]:
        """Генерация с fallback"""
        if self.use_transformers and self.transformer_service:
            try:
                return self.transformer_service.generate_embedding(text)
            except Exception as e:
                print(f"⚠️ Transformer failed: {e}, using fallback")
                if self.fallback_service:
                    return self.fallback_service._generate_improved_embedding(text)

        if self.fallback_service:
            return self.fallback_service._generate_improved_embedding(text)

        raise ValueError("No embedding service available")

    def generate_embeddings_batch(
            self,
            texts: List[str]
    ) -> List[List[float]]:
        """Пакетная генерация с fallback"""
        if self.use_transformers and self.transformer_service:
            try:
                return self.transformer_service.generate_embeddings_batch(texts)
            except Exception as e:
                print(f"⚠️ Transformer batch failed: {e}, using fallback")

        # Fallback: генерируем по одному
        if self.fallback_service:
            return [
                self.fallback_service._generate_improved_embedding(text)
                for text in texts
            ]

        raise ValueError("No embedding service available")


# ============================================================================
# Интеграция в improved_preprocessing_service.py
# ============================================================================

"""
Для использования добавьте в improved_preprocessing_service.py:

1. В __init__:

def __init__(self, data_adapter, use_transformer_embeddings: bool = False):
    self.data_adapter = data_adapter
    self.stop_words = {...}

    # ДОБАВЬТЕ ЭТО:
    self.use_transformer_embeddings = use_transformer_embeddings

    if use_transformer_embeddings:
        try:
            from .advanced_embedding_service import AdvancedEmbeddingService
            self.embedding_service = AdvancedEmbeddingService()
            print("✅ Используются transformer embeddings")
        except ImportError:
            print("⚠️ sentence-transformers не установлен, используются легковесные")
            self.embedding_service = None
            self.use_transformer_embeddings = False
    else:
        self.embedding_service = None


2. В методе preprocess_solution замените:

# Было:
embedding = self._generate_improved_embedding(text)

# Стало:
if self.use_transformer_embeddings and self.embedding_service:
    embedding = self.embedding_service.generate_embedding(text)
else:
    embedding = self._generate_improved_embedding(text)


3. Для активации в laboratory_service.py:

# В get_laboratory_service():
preprocessing_service = ImprovedPreprocessingService(
    data_adapter,
    use_transformer_embeddings=True  # ВКЛЮЧИТЬ ЗДЕСЬ
)
"""


# ============================================================================
# Утилиты для миграции и тестирования
# ============================================================================

class EmbeddingMigrationHelper:
    """
    Помощник для миграции с легковесных на transformer embeddings

    Позволяет постепенно мигрировать существующие записи
    """

    def __init__(
            self,
            data_adapter,
            batch_size: int = 50
    ):
        self.data_adapter = data_adapter
        self.batch_size = batch_size
        self.embedding_service = AdvancedEmbeddingService()

    async def migrate_all_embeddings(self):
        """
        Мигрировать все существующие embeddings на transformer версии

        ВНИМАНИЕ: Это может занять время для больших баз
        """
        from datastorage.crud.datastorage import CRUDDataStorage
        from datastorage.database.models import SolutionPreprocessing

        ds = CRUDDataStorage(
            model=SolutionPreprocessing,
            session=self.data_adapter.session
        )

        # Получаем все предобработки
        all_preps = await ds.list()

        print(f"🔄 Начинаю миграцию {len(all_preps)} embeddings...")

        migrated = 0
        errors = 0

        for i in range(0, len(all_preps), self.batch_size):
            batch = all_preps[i:i + self.batch_size]

            for prep in batch:
                try:
                    # Получаем решение
                    solution = prep.solution
                    if not solution:
                        continue

                    # Генерируем новый embedding
                    new_embedding = self.embedding_service.generate_embedding(
                        solution.current_content
                    )

                    # Обновляем
                    prep.embedding = json.dumps(new_embedding)
                    migrated += 1

                except Exception as e:
                    print(f"❌ Ошибка для {prep.solution_id}: {e}")
                    errors += 1

            # Коммитим батч
            await self.data_adapter.session.commit()
            print(
                f"  Обработано: {min(i + self.batch_size, len(all_preps))} / {len(all_preps)}")

        print(f"✅ Миграция завершена: {migrated} успешно, {errors} ошибок")

        return {
            "total": len(all_preps),
            "migrated": migrated,
            "errors": errors
        }

    async def compare_quality(self, solution_id: str, top_k: int = 10):
        """
        Сравнить качество легковесных vs transformer embeddings

        Показывает насколько улучшится качество поиска
        """
        # Получаем целевое решение
        solution = await self.data_adapter.get_solution(solution_id)
        if not solution:
            raise ValueError("Решение не найдено")

        # Генерируем оба типа embeddings
        text = solution.current_content

        # Легковесный (из improved_preprocessing)
        from .preprocessing_service import PreprocessingService
        lightweight_service = PreprocessingService(self.data_adapter)
        lightweight_emb = lightweight_service._generate_improved_embedding(text)

        # Transformer
        transformer_emb = self.embedding_service.generate_embedding(text)

        # Получаем все другие решения
        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        # Генерируем embeddings для всех
        other_texts = [s.current_content for s in other_solutions]

        lightweight_others = [
            lightweight_service._generate_improved_embedding(t)
            for t in other_texts
        ]

        transformer_others = self.embedding_service.generate_embeddings_batch(
            other_texts
        )

        # Находим топ-K для каждого
        def find_similar(query_emb, candidate_embs):
            query = np.array(query_emb)
            candidates = np.array(candidate_embs)
            similarities = np.dot(candidates, query) / (
                    np.linalg.norm(candidates, axis=1) * np.linalg.norm(query)
            )
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            return [(int(idx), float(similarities[idx])) for idx in top_indices]

        lightweight_results = find_similar(lightweight_emb, lightweight_others)
        transformer_results = find_similar(transformer_emb, transformer_others)

        # Сравниваем
        print("\n📊 Сравнение качества embeddings:")
        print("\n1️⃣ Легковесные (TF-IDF + n-grams):")
        for idx, score in lightweight_results[:5]:
            sol = other_solutions[idx]
            print(
                f"   {score:.3f} - {sol.id[:8]}... ({len(sol.current_content)} символов)")

        print("\n2️⃣ Transformer (all-MiniLM-L6-v2):")
        for idx, score in transformer_results[:5]:
            sol = other_solutions[idx]
            print(
                f"{score:.3f} - {sol.id[:8]}... ({len(sol.current_content)} символов)"
            )

        # Метрики
        overlap = len(set([r[0] for r in lightweight_results]) &
                      set([r[0] for r in transformer_results]))

        print(f"\n📈 Метрики:")
        print(
            f"Пересечение топ-{top_k}: {overlap}/{top_k} ({overlap / top_k * 100:.1f}%)"
        )
        print(
            f"Средняя similarity (легковесные): {np.mean([s for _, s in lightweight_results]):.3f}"
        )
        print(
            f"Средняя similarity (transformer): {np.mean([s for _, s in transformer_results]):.3f}"
        )

        return {
            "lightweight_results": lightweight_results,
            "transformer_results": transformer_results,
            "overlap": overlap,
            "overlap_percent": overlap / top_k * 100
        }


# ============================================================================
# Готовая интеграция для production
# ============================================================================

def create_embedding_service(use_transformers: bool = False):
    """
    Фабрика для создания embedding сервиса

    Args:
        use_transformers: Если True - использует sentence-transformers

    Returns:
        Сервис для генерации embeddings
    """
    if use_transformers and SENTENCE_TRANSFORMERS_AVAILABLE:
        return AdvancedEmbeddingService()
    else:
        # Fallback на легковесные
        return None  # Будет использован метод из ImprovedPreprocessingService


# Singleton для transformer сервиса
_transformer_service_instance: Optional[AdvancedEmbeddingService] = None


def get_transformer_embedding_service() -> Optional[AdvancedEmbeddingService]:
    """Получение singleton instance transformer сервиса"""
    global _transformer_service_instance

    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None

    if _transformer_service_instance is None:
        _transformer_service_instance = AdvancedEmbeddingService()

    return _transformer_service_instance
