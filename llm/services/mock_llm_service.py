import asyncio
from typing import List, Dict, Any, Optional

from entities.challenge.model import Challenge
from entities.solution.model import Solution
from llm.models.lab import (
    LLMProvider, ThinkingDirection,
    CollectiveIdea, ImprovementSuggestion, CriticismPoint
)
from llm.services.llm_service import LLMService


class MockLLMService(LLMService):
    """Mock версия LLM сервиса для отладки"""

    def __init__(self, providers: List[LLMProvider] = None):
        self.providers = providers or []
        self.session = None

    async def generate_thinking_directions(
            self,
            challenge: Challenge,
            existing_solutions: List[Solution],
            max_directions: int = 5
    ) -> List[ThinkingDirection]:
        """Mock направления мысли"""
        await asyncio.sleep(1.0)

        return [
            ThinkingDirection(
                title="Технологический подход",
                description="Решение проблемы через внедрение новых технологий",
                key_approaches=["IoT решения", "Автоматизация",
                                "ИИ-алгоритмы"],
                participants_count=8,
                initial_solution_text="Предлагаю сосредоточиться на внедрении умных технологий для оптимизации процессов. Основная идея заключается в создании интегрированной системы, которая будет автоматически анализировать данные и предлагать решения в режиме реального времени. Это позволит значительно повысить эффективность и снизить человеческий фактор в критических процессах.",
                example_excerpts=["умные сенсоры", "машинное обучение",
                                  "предиктивная аналитика"]
            ),
            ThinkingDirection(
                title="Социально-экономический подход",
                description="Изменение системы стимулов и мотиваций",
                key_approaches=["Изменение стимулов",
                                "Новые модели финансирования", "Партнерства"],
                participants_count=5,
                initial_solution_text="Считаю, что корень проблемы лежит в неправильных стимулах участников системы. Необходимо пересмотреть экономические механизмы и создать такую систему мотивации, при которой всем участникам будет выгодно действовать в общих интересах. Это может включать новые модели оплаты, государственно-частные партнерства и инновационные схемы распределения ресурсов.",
                example_excerpts=["система стимулов",
                                  "экономические механизмы", "общие интересы"]
            ),
            ThinkingDirection(
                title="Процессный подход",
                description="Оптимизация существующих процессов и workflows",
                key_approaches=["Реинжиниринг процессов", "Стандартизация", "Измерение KPI"],
                participants_count=6,
                initial_solution_text="Проблему нужно решать через кардинальную перестройку существующих процессов. Предлагаю провести полный аудит текущих workflow, выявить узкие места и неэффективности, а затем спроектировать оптимизированные процессы с четкими метриками успеха. Ключевой момент - стандартизация и автоматизация рутинных операций.",
                example_excerpts=["аудит процессов", "узкие места", "стандартизация"]
            )
        ]

    async def generate_collective_ideas(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_ideas: int = 3
    ) -> List[CollectiveIdea]:
        """Mock идеи"""
        await asyncio.sleep(1.0)

        return [
            CollectiveIdea(
                idea_description="Интеграция блокчейн-технологии для обеспечения прозрачности процессов",
                combination_elements=[
                    {
                        "element": "Децентрализованное управление",
                        "solution_id": "4447a1d1-7029-4624-8c15-2c1e52e0b4ba",
                        "reasoning": "Логика появления этого элемента"
                    },
                    {
                        "element": "Децентрализованное управление",
                        "solution_id": "4447a1d1-7029-4624-8c15-2c1e52e0b4ba",
                        "reasoning": "Логика появления этого элемента"
                    },
                ],
                source_solutions_count=2,
                potential_impact="Повышение доверия участников и исключение манипуляций",
                reasoning="Блокчейн обеспечит неизменяемость записей и прозрачность всех операций"
            ),
            CollectiveIdea(
                idea_description="Создание гибридной модели с элементами краудсорсинга",
                combination_elements=[
                    {
                        "element": "Коллективные решения",
                        "solution_id": "4447a1d1-7029-4624-8c15-2c1e52e0b4ba",
                        "reasoning": "Логика появления этого элемента"
                    },
                    {
                        "element": "Экспертная валидация",
                        "solution_id": "4447a1d1-7029-4624-8c15-2c1e52e0b4ba",
                        "reasoning": "Логика появления этого элемента"
                    },
                ],
                source_solutions_count=2,
                potential_impact="Использование коллективного интеллекта при сохранении качества",
                reasoning="Сочетание массового участия с экспертным контролем даст лучший результат"
            )
        ]

    async def generate_improvement_suggestions(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_suggestions: int = 4
    ) -> List[ImprovementSuggestion]:
        """Mock предложения по улучшению"""
        await asyncio.sleep(0.8)

        return [
            ImprovementSuggestion(
                target_element="Система мониторинга",
                improvement_description="Добавить real-time dashboard с ключевыми метриками",
                integration_advice="Интегрировать после блока про сбор данных, перед анализом результатов",
                source_examples=["Решение участника А: интерактивные дашборды",
                                 "Решение Б: live-метрики"],
                reasoning="Визуализация в реальном времени поможет быстрее выявлять проблемы"
            ),
            ImprovementSuggestion(
                target_element="Система обратной связи",
                improvement_description="Внедрить многоуровневую систему feedback от разных групп пользователей",
                integration_advice="Добавить в раздел о взаимодействии с пользователями",
                source_examples=[
                    "Решение №8: сегментированная обратная связь"],
                reasoning="Разные группы пользователей дадут более полную картину эффективности решения"
            )
        ]

    async def generate_solution_criticism(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_criticisms: int = 3
    ) -> List[CriticismPoint]:
        """Mock критика"""
        await asyncio.sleep(0.7)

        return [
            CriticismPoint(
                criticism_text="Недостаточно внимания уделено вопросам масштабируемости решения",
                severity="major",
                evidence=["Решение №4 показывает проблемы роста",
                          "Опыт №11 с перегрузками системы"],
                suggested_fix="Добавить раздел про архитектуру для высоких нагрузок и план поэтапного масштабирования",
                reasoning="Без планирования масштабирования решение может не справиться с ростом нагрузки"
            ),
            CriticismPoint(
                criticism_text="Слабо проработаны вопросы безопасности данных",
                severity="critical",
                evidence=["Решение №6 детально разбирает угрозы безопасности"],
                suggested_fix="Включить анализ рисков безопасности и описание мер защиты",
                reasoning="Безопасность критически важна для доверия пользователей и соответствия регуляторным требованиям"
            )
        ]

    async def integrate_accepted_items(
            self,
            current_solution: Solution,
            accepted_items: List[Dict[str, Any]],
            user_modifications: Optional[List[str]] = None
    ) -> str:
        """Mock интеграция"""
        await asyncio.sleep(1.2)

        return f"""[ОБНОВЛЕННОЕ РЕШЕНИЕ]

            {current_solution.current_content}
            
            [ДОБАВЛЕНО: Блокчейн-интеграция]
            Для обеспечения прозрачности и неизменяемости данных предлагается интегрировать блокчейн-решение, которое будет фиксировать все ключевые операции и решения в распределенном реестре.
            
            [ИЗМЕНЕНО: Система мониторинга]
            Система мониторинга дополнена real-time dashboard с интерактивными метриками, позволяющими отслеживать эффективность решения в режиме реального времени.
            
            [ДОБАВЛЕНО: Планирование масштабирования]
            Включен детальный план поэтапного масштабирования решения с учетом роста нагрузки и количества пользователей.
            """