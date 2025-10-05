import pytest
from unittest.mock import Mock, patch

from llm.services.preprocessing_service import PreprocessingService
from llm.services.cache_service import SemanticCache
from llm.services.llm_service import LLMService
from llm.models.lab import LLMProvider


# ============================================================================
# ФИКСТУРЫ
# ============================================================================

@pytest.fixture
def mock_solution():
    """Мок Solution объекта"""
    solution = Mock()
    solution.id = "test-solution-id"
    solution.challenge_id = "test-challenge-id"
    solution.user_id = "test-user-id"
    solution.current_content = """
    Предлагаю решить проблему через внедрение автоматизации.
    Основная идея - создать умную систему мониторинга, которая 
    будет анализировать данные в режиме реального времени.
    Это позволит быстро выявлять проблемы и принимать решения.
    """
    return solution


@pytest.fixture
def mock_challenge():
    """Мок Challenge объекта"""
    challenge = Mock()
    challenge.id = "test-challenge-id"
    challenge.title = "Улучшение системы транспорта"
    challenge.description = "Как улучшить общественный транспорт в городе"
    challenge.community_id = "test-community-id"
    return challenge


@pytest.fixture
def mock_data_adapter():
    """Мок DataAdapter"""
    adapter = Mock()
    adapter.session = Mock()
    return adapter


@pytest.fixture
def preprocessing_service(mock_data_adapter):
    """PreprocessingService для тестов"""
    return PreprocessingService(mock_data_adapter)


@pytest.fixture
def cache_service():
    """SemanticCache для тестов"""
    return SemanticCache(max_size=100, similarity_threshold=0.9)


# ============================================================================
# ТЕСТЫ PREPROCESSING SERVICE
# ============================================================================

class TestPreprocessing:
    """Тесты предобработки решений"""

    def test_tokenize(self, preprocessing_service):
        """Тест токенизации текста"""
        text = "Это тест, проверка токенизации! Работает?"
        tokens = preprocessing_service._tokenize(text)

        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "тест" in tokens
        assert "проверка" in tokens

    def test_extract_key_points(self, preprocessing_service):
        """Тест извлечения ключевых тезисов"""
        text = """
        Первое предложение с важной мыслью.
        Второе предложение развивает идею дальше.
        Третье предложение добавляет детали.
        Четвертое предложение заключает все вместе.
        """

        key_points = preprocessing_service._extract_key_points(text,
                                                               max_sentences=2)

        assert isinstance(key_points, str)
        assert len(key_points) > 0
        # Должно содержать не более 2-3 предложений
        assert key_points.count('.') <= 3

    def test_classify_approach_technical(self, preprocessing_service,
                                         mock_challenge):
        """Тест классификации технического подхода"""
        text = """
        Предлагаю внедрить IoT сенсоры и систему автоматизации.
        Использовать машинное обучение для анализа данных.
        Создать API для интеграции с существующими системами.
        """

        category = preprocessing_service._classify_approach(text,
                                                            mock_challenge)

        assert category == "technical"

    def test_classify_approach_social(self, preprocessing_service,
                                      mock_challenge):
        """Тест классификации социального подхода"""
        text = """
        Необходимо изменить систему мотивации участников.
        Создать партнерства между разными группами.
        Улучшить коммуникацию внутри сообщества.
        """

        category = preprocessing_service._classify_approach(text,
                                                            mock_challenge)

        assert category == "social"

    def test_calculate_metrics(self, preprocessing_service):
        """Тест расчета метрик"""
        text = """
        Первый абзац с важной информацией.
        Содержит несколько предложений для анализа.

        Второй абзац продолжает мысль.
        """

        metrics = preprocessing_service._calculate_metrics(text)

        assert "length" in metrics
        assert "word_count" in metrics
        assert "sentence_count" in metrics
        assert "structure_score" in metrics

        assert metrics["length"] > 0
        assert metrics["word_count"] > 0
        assert 0 <= metrics["structure_score"] <= 1

    def test_generate_simple_embedding(self, preprocessing_service):
        """Тест генерации простого embedding"""
        text = "Тестовый текст для генерации embedding"

        embedding = preprocessing_service._generate_simple_embedding(text,
                                                                     dim=128)

        assert isinstance(embedding, list)
        assert len(embedding) == 128
        assert all(isinstance(x, float) for x in embedding)

        # Embedding должен быть нормализован
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert 0.99 <= norm <= 1.01  # Примерно 1


# ============================================================================
# ТЕСТЫ CACHE SERVICE
# ============================================================================

class TestCacheService:
    """Тесты semantic cache"""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache_service):
        """Тест сохранения и получения из кэша"""
        solution_id = "test-solution-1"
        request_type = "ideas"
        other_ids = ["sol-2", "sol-3", "sol-4"]

        test_value = {"ideas": ["idea1", "idea2"], "count": 2}

        # Сохраняем
        await cache_service.set(
            solution_id, request_type, other_ids, test_value
        )

        # Получаем
        cached = await cache_service.get(
            solution_id, request_type, other_ids
        )

        assert cached is not None
        assert cached == test_value

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_service):
        """Тест cache miss"""
        result = await cache_service.get(
            "nonexistent", "ideas", ["sol-1"]
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_similarity(self, cache_service):
        """Тест поиска похожих запросов"""
        # Понижаем threshold для теста
        cache_service.similarity_threshold = 0.7

        # Сохраняем
        await cache_service.set(
            "sol-1", "ideas", ["sol-2", "sol-3", "sol-4"],
            {"test": "value1"}
        )

        # Пытаемся получить с немного другими параметрами
        # (другой порядок, но те же ID)
        cached = await cache_service.get(
            "sol-1", "ideas", ["sol-3", "sol-2", "sol-4"]
        )

        # Должны найти благодаря similarity
        assert cached is not None

    def test_cache_stats(self, cache_service):
        """Тест статистики кэша"""
        stats = cache_service.get_stats()

        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate_percent" in stats

    @pytest.mark.asyncio
    async def test_cache_eviction(self):
        """Тест вытеснения старых записей"""
        small_cache = SemanticCache(max_size=5)

        # Заполняем кэш
        for i in range(10):
            await small_cache.set(
                f"sol-{i}", "ideas", [f"other-{i}"],
                {"value": i}
            )

        # Размер не должен превышать max_size
        assert len(small_cache.cache) <= 5


# ============================================================================
# ТЕСТЫ LLM SERVICE
# ============================================================================

class TestLLMService:
    """Тесты LLM сервиса"""

    def test_provider_priority_sorting(self):
        """Тест сортировки провайдеров по приоритету"""
        providers = [
            LLMProvider(
                name="low", api_url="url", model="model",
                max_tokens=1000, priority=3
            ),
            LLMProvider(
                name="high", api_url="url", model="model",
                max_tokens=1000, priority=1
            ),
            LLMProvider(
                name="medium", api_url="url", model="model",
                max_tokens=1000, priority=2
            ),
        ]

        llm_service = LLMService(providers)

        # Провайдеры должны быть отсортированы по priority
        assert llm_service.providers[0].name == "high"
        assert llm_service.providers[1].name == "medium"
        assert llm_service.providers[2].name == "low"

    def test_parse_json_response(self):
        """Тест парсинга JSON ответа"""
        # Ответ с обрамляющим текстом
        response_text = """
        Вот результат:
        {
          "ideas": [
            {"description": "Идея 1"},
            {"description": "Идея 2"}
          ]
        }
        Это все.
        """

        result = LLMService._parse_response(response_text, "json")

        assert "ideas" in result
        assert len(result["ideas"]) == 2

    def test_format_solutions_for_analysis(self, mock_solution):
        """Тест форматирования решений для анализа"""
        solutions = [mock_solution for _ in range(5)]

        formatted = LLMService._format_solutions_for_analysis(solutions)

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "РЕШЕНИЕ #1" in formatted
        assert "РЕШЕНИЕ #5" in formatted


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    async def test_preprocessing_pipeline(
            self,
            preprocessing_service,
            mock_solution,
            mock_challenge
    ):
        """Тест полного пайплайна предобработки"""
        # Мокаем создание в БД
        with patch.object(
                preprocessing_service.data_adapter,
                'session',
                Mock()
        ):
            result = await preprocessing_service.preprocess_solution(
                mock_solution, mock_challenge
            )

            assert "embedding" in result
            assert "key_points" in result
            assert "category" in result
            assert "metrics" in result

            assert len(result["embedding"]) > 0
            assert len(result["key_points"]) > 0
            assert result["category"] in [
                "technical", "social", "creative",
                "analytical", "practical", "general"
            ]


# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])