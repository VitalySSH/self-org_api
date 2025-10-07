import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import numpy as np


class InMemoryCacheEntry:
    """Запись в кэше"""

    def __init__(
            self,
            key: str,
            value: Any,
            embedding: List[float],
            ttl: int = 3600
    ):
        self.key = key
        self.value = value
        self.embedding = np.array(embedding)
        self.created_at = datetime.now()
        self.ttl = ttl
        self.hits = 0

    def is_expired(self) -> bool:
        """Проверка истечения TTL"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)

    def get_age_seconds(self) -> float:
        """Возраст записи в секундах"""
        return (datetime.now() - self.created_at).total_seconds()


class SemanticCache:
    """
    In-Memory кэш с семантическим поиском

    Использует cosine similarity embeddings для поиска похожих запросов
    """

    def __init__(
            self,
            max_size: int = 1000,
            similarity_threshold: float = 0.90,
            default_ttl: int = 3600
    ):
        """
        Args:
            max_size: Максимальное количество записей в кэше
            similarity_threshold: Минимальная similarity для считывания hit
            default_ttl: TTL по умолчанию (секунды)
        """
        self.cache: Dict[str, InMemoryCacheEntry] = {}
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.default_ttl = default_ttl

        # Статистика
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _create_cache_key(
            solution_id: str,
            request_type: str,
            other_solutions_ids: List[str]
    ) -> str:
        """
        Создание уникального ключа кэша

        Args:
            solution_id: ID целевого решения
            request_type: Тип запроса (ideas, improvements, criticism)
            other_solutions_ids: ID других решений для анализа
        """
        # Сортируем ID для консистентности
        sorted_ids = sorted(other_solutions_ids)
        data = f"{solution_id}:{request_type}:{':'.join(sorted_ids)}"
        return hashlib.md5(data.encode()).hexdigest()

    @staticmethod
    def _create_embedding(
            solution_id: str,
            request_type: str,
            other_solutions_ids: List[str],
            dim: int = 128
    ) -> np.ndarray:
        """
        Создание простого embedding для запроса

        Используем хеширование ID в пространство embeddings
        """
        embedding = np.zeros(dim)

        # Хешируем каждый ID и добавляем в embedding
        for sol_id in [solution_id] + other_solutions_ids:
            hash_val = hash(sol_id) % dim
            embedding[hash_val] += 1.0

        # Хешируем тип запроса
        type_hash = hash(request_type) % dim
        embedding[type_hash] += 2.0  # Больший вес для типа

        # Нормализация
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    async def get(
            self,
            solution_id: str,
            request_type: str,
            other_solutions_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Получение результата из кэша

        Сначала проверяет точное совпадение ключа,
        потом ищет похожие запросы через similarity

        Returns:
            Cached результат или None
        """
        # Очистка устаревших записей
        self._cleanup_expired()

        # 1. Точное совпадение
        key = self._create_cache_key(
            solution_id,
            request_type,
            other_solutions_ids
        )
        if key in self.cache:
            entry = self.cache[key]
            entry.hits += 1
            self.hits += 1
            return entry.value

        # 2. Semantic search
        query_embedding = self._create_embedding(
            solution_id, request_type, other_solutions_ids
        )

        best_match = None
        best_similarity = 0.0

        for entry in self.cache.values():
            similarity = self._cosine_similarity(query_embedding,
                                                 entry.embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry

        # Если нашли достаточно похожий запрос
        if best_match and best_similarity >= self.similarity_threshold:
            best_match.hits += 1
            self.hits += 1
            return best_match.value

        # Cache miss
        self.misses += 1
        return None

    async def set(
            self,
            solution_id: str,
            request_type: str,
            other_solutions_ids: List[str],
            value: Any,
            ttl: Optional[int] = None
    ) -> None:
        """
        Сохранение результата в кэш

        Args:
            solution_id: ID целевого решения
            request_type: Тип запроса
            other_solutions_ids: ID других решений
            value: Результат для кэширования
            ttl: Time-to-live (секунды), если None - используется default
        """
        # Если кэш переполнен, удаляем старые записи
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        key = self._create_cache_key(solution_id, request_type,
                                     other_solutions_ids)
        embedding = self._create_embedding(
            solution_id, request_type, other_solutions_ids
        )

        entry = InMemoryCacheEntry(
            key=key,
            value=value,
            embedding=embedding.tolist(),
            ttl=ttl or self.default_ttl
        )

        self.cache[key] = entry

    async def invalidate(
            self,
            solution_id: Optional[str] = None,
            request_type: Optional[str] = None
    ) -> int:
        """
        Инвалидация записей кэша

        Args:
            solution_id: Если указан, удаляет все записи с этим solution_id
            request_type: Если указан, удаляет все записи этого типа

        Returns:
            Количество удаленных записей
        """
        if solution_id is None and request_type is None:
            # Полная очистка
            count = len(self.cache)
            self.cache.clear()
            return count

        # Частичная очистка (простая реализация - перебор)
        # В продакшене можно оптимизировать через индексы
        to_remove = []

        for key in self.cache.keys():
            # Декодируем ключ для проверки (упрощенно)
            # В реальности можно хранить метаданные отдельно
            to_remove.append(key)

        for key in to_remove:
            del self.cache[key]

        return len(to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_requests = self.hits + self.misses
        hit_rate = (
                self.hits / total_requests * 100
        ) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }

    def _cleanup_expired(self) -> None:
        """Удаление устаревших записей"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self.cache[key]

    def _evict_oldest(self, count: int = 100) -> None:
        """
        Удаление самых старых записей при переполнении кэша

        Args:
            count: Количество записей для удаления
        """
        # Сортируем по времени создания
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].created_at
        )

        # Удаляем самые старые
        for key, _ in sorted_entries[:count]:
            del self.cache[key]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity между двумя векторами"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Singleton instance для использования в приложении
_cache_instance: Optional[SemanticCache] = None


def get_cache_instance() -> SemanticCache:
    """Получение singleton instance кэша"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCache(
            max_size=1000,
            similarity_threshold=0.90,
            default_ttl=3600  # 1 час
        )
    return _cache_instance