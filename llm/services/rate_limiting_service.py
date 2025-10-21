from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from threading import Lock

from core.config import LLM_RATE_LIMIT_SECONDS


@dataclass
class RateLimitEntry:
    """Запись о последнем запросе пользователя"""
    user_id: str
    request_type: str
    timestamp: datetime

    def is_expired(self, ttl_seconds: int = 1800) -> bool:
        """Проверка истечения времени ограничения"""
        return datetime.now() > self.timestamp + timedelta(seconds=ttl_seconds)

    def seconds_remaining(self, ttl_seconds: int = 1800) -> int:
        """Возвращает оставшееся время до разблокировки"""
        expires_at = self.timestamp + timedelta(seconds=ttl_seconds)
        remaining = (expires_at - datetime.now()).total_seconds()
        return max(0, int(remaining))


class RateLimitingService:
    """
    In-Memory Rate Limiting для запросов к LLM

    Ограничивает пользователя: 1 запрос каждого типа в течение 30 минут
    """

    def __init__(self, ttl_seconds: int = 1800):
        """
        Args:
            ttl_seconds: Время блокировки в секундах (по умолчанию 30 минут)
        """
        self.ttl_seconds = ttl_seconds
        self._storage: Dict[str, RateLimitEntry] = {}
        self._lock = Lock()

    def _make_key(self, user_id: str, request_type: str) -> str:
        """Создание ключа для хранения"""
        return f"{user_id}:{request_type}"

    def check_rate_limit(
            self,
            user_id: str,
            request_type: str
    ) -> Tuple[bool, Optional[int]]:
        """
        Проверка rate limit для пользователя

        Args:
            user_id: ID пользователя
            request_type: Тип запроса (ideas, improvements, criticism, directions)

        Returns:
            Tuple[allowed: bool, seconds_remaining: Optional[int]]
            - allowed: True если запрос разрешён
            - seconds_remaining: None если разрешён, иначе количество секунд до разблокировки
        """
        key = self._make_key(user_id, request_type)

        with self._lock:
            # Очистка устаревших записей
            self._cleanup_expired()

            if key in self._storage:
                entry = self._storage[key]
                if not entry.is_expired(self.ttl_seconds):
                    # Запрос ещё заблокирован
                    seconds_remaining = entry.seconds_remaining(self.ttl_seconds)
                    return False, seconds_remaining

            # Запрос разрешён
            return True, None

    def record_request(self, user_id: str, request_type: str) -> None:
        """
        Записать факт выполнения запроса

        Args:
            user_id: ID пользователя
            request_type: Тип запроса
        """
        key = self._make_key(user_id, request_type)

        with self._lock:
            self._storage[key] = RateLimitEntry(
                user_id=user_id,
                request_type=request_type,
                timestamp=datetime.now()
            )

    def _cleanup_expired(self) -> None:
        """Удаление устаревших записей"""
        expired_keys = [
            key for key, entry in self._storage.items()
            if entry.is_expired(self.ttl_seconds)
        ]

        for key in expired_keys:
            del self._storage[key]

    def get_stats(self) -> Dict[str, int]:
        """Получение статистики (для мониторинга)"""
        with self._lock:
            self._cleanup_expired()
            return {
                "active_limits": len(self._storage),
                "ttl_seconds": self.ttl_seconds
            }

    def clear_user_limits(self, user_id: str) -> int:
        """
        Очистить все ограничения для пользователя (для админских целей)

        Returns:
            Количество удалённых записей
        """
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._storage.items()
                if entry.user_id == user_id
            ]

            for key in keys_to_remove:
                del self._storage[key]

            return len(keys_to_remove)


# Singleton instance
_rate_limiting_instance: Optional[RateLimitingService] = None


def get_rate_limiting_service() -> RateLimitingService:
    """Получение singleton instance rate limiting сервиса"""
    global _rate_limiting_instance
    if _rate_limiting_instance is None:
        _rate_limiting_instance = RateLimitingService(
            ttl_seconds=LLM_RATE_LIMIT_SECONDS
        )
    return _rate_limiting_instance
