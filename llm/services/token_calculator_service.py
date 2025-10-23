from typing import List, Dict, Any, Optional
import tiktoken
from llm.models.lab import LLMProvider


class TokenCalculatorService:
    """
    Сервис для динамического расчёта токенов

    Оптимально рассчитывает максимальное количество токенов для ответа
    на основе размера контекста и лимитов провайдера
    """

    def __init__(self):
        # Используем кодировщик для llama/mistral моделей
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except KeyError:
            # Fallback на cl100k_base если модель не найдена
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Подсчёт количества токенов в тексте

        Args:
            text: Текст для подсчёта

        Returns:
            Количество токенов
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def calculate_optimal_max_tokens(
            self,
            provider: LLMProvider,
            system_prompt: str,
            user_prompt: str,
            safety_margin: float = 0.15
    ) -> Dict[str, Any]:
        """
        Рассчитывает оптимальное количество токенов для ответа

        Args:
            provider: Конфигурация LLM провайдера
            system_prompt: Системный промпт
            user_prompt: Промпт пользователя
            safety_margin: Запас для вариативности токенизации (15% по умолчанию)

        Returns:
            Dict с информацией:
            - max_tokens: оптимальное количество токенов для ответа
            - context_tokens: токены в контексте
            - available_tokens: доступные токены
            - fits_in_context: влезает ли в контекст
            - truncation_needed: нужна ли обрезка
        """
        # Считаем токены в промптах
        system_tokens = self.count_tokens(system_prompt)
        user_tokens = self.count_tokens(user_prompt)
        context_tokens = system_tokens + user_tokens

        # Добавляем запас на вариативность токенизации между моделями
        context_tokens_with_margin = int(context_tokens * (1 + safety_margin))

        # ИСПРАВЛЕНИЕ: Для Together AI есть ограничение inputs + max_new_tokens <= max_context_tokens
        # Поэтому доступные токены = max_context_tokens - context_tokens_with_margin
        available_for_response = provider.max_context_tokens - context_tokens_with_margin

        # Проверяем влезает ли вообще
        fits_in_context = context_tokens_with_margin < provider.max_context_tokens

        if available_for_response < 600:
            # Если доступно совсем мало - пробуем использовать минимум
            optimal_max_tokens = 600
        else:
            optimal_max_tokens = min(
                provider.max_tokens,
                available_for_response,
                6000
            )

        return {
            "max_tokens": optimal_max_tokens,
            "context_tokens": context_tokens,
            "context_tokens_with_margin": context_tokens_with_margin,
            "available_tokens": available_for_response,
            "fits_in_context": fits_in_context,
            "provider_max_context": provider.max_context_tokens,
            "provider_max_tokens": provider.max_tokens,
            "truncation_needed": not fits_in_context
        }

    def calculate_max_solutions_fit(
            self,
            provider: LLMProvider,
            system_prompt: str,
            base_prompt: str,
            solution_texts: List[str],
            safety_margin: float = 0.15,
            min_response_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Рассчитывает сколько решений влезет в контекст

        Args:
            provider: Конфигурация провайдера
            system_prompt: Системный промпт
            base_prompt: Базовый промпт (без решений)
            solution_texts: Список текстов решений
            safety_margin: Запас на вариативность
            min_response_tokens: Минимум токенов для ответа

        Returns:
            Dict с информацией:
            - max_solutions_count: максимальное количество решений
            - solutions_fit: список индексов решений которые влезли
            - total_tokens: общее количество токенов
            - response_tokens: токены для ответа
        """
        system_tokens = self.count_tokens(system_prompt)
        base_tokens = self.count_tokens(base_prompt)

        # Токены которые нужно зарезервировать
        reserved_tokens = int((system_tokens + base_tokens) * (1 + safety_margin))
        reserved_tokens += min_response_tokens

        # Доступные токены для решений
        available_for_solutions = provider.max_context_tokens - reserved_tokens

        if available_for_solutions <= 0:
            return {
                "max_solutions_count": 0,
                "solutions_fit": [],
                "total_tokens": reserved_tokens,
                "response_tokens": 0,
                "error": "Базовый контекст не влезает в лимиты провайдера"
            }

        # Подбираем количество решений
        solutions_fit = []
        accumulated_tokens = 0

        for idx, solution_text in enumerate(solution_texts):
            solution_tokens = self.count_tokens(solution_text)

            # Добавляем запас на форматирование (заголовки, разделители)
            solution_tokens_with_overhead = int(solution_tokens * 1.05) + 50

            if accumulated_tokens + solution_tokens_with_overhead <= available_for_solutions:
                solutions_fit.append(idx)
                accumulated_tokens += solution_tokens_with_overhead
            else:
                break

        total_tokens = reserved_tokens + accumulated_tokens
        response_tokens = provider.max_context_tokens - total_tokens

        return {
            "max_solutions_count": len(solutions_fit),
            "solutions_fit": solutions_fit,
            "total_tokens": total_tokens,
            "response_tokens": min(response_tokens, provider.max_tokens),
            "available_for_solutions": available_for_solutions,
            "used_solution_tokens": accumulated_tokens
        }

    @staticmethod
    def optimize_solution_texts(
            solutions: List[Any],
            max_solutions: int,
    ) -> List[str]:
        """
        Оптимизирует тексты решений для анализа

        Args:
            solutions: Список объектов Solution
            max_solutions: Максимальное количество решений
            max_chars_per_solution: Максимум символов на решение

        Returns:
            Список оптимизированных текстов
        """
        optimized_texts = []

        for solution in solutions[:max_solutions]:
            content = solution.current_content

            optimized_texts.append(content)

        return optimized_texts


# Singleton instance
_token_calculator_instance: Optional[TokenCalculatorService] = None


def get_token_calculator() -> TokenCalculatorService:
    """Получение singleton instance калькулятора токенов"""
    global _token_calculator_instance
    if _token_calculator_instance is None:
        _token_calculator_instance = TokenCalculatorService()
    return _token_calculator_instance
