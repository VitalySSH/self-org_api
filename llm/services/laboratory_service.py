from typing import List, Dict, Any, Optional
from datetime import datetime

from .llm_service import LLMService, ThinkingDirection
from ..adapters.data_adapter import DataAdapter


class LaboratoryService:
    """Основной сервис лаборатории коллективного интеллекта"""

    def __init__(self, data_adapter: DataAdapter, llm_service: LLMService):
        self.data_adapter = data_adapter
        self.llm_service = llm_service

    # === Работа с направлениями мысли ===

    async def generate_thinking_directions(
            self,
            challenge_id: str,
            user_id: str
    ) -> List[ThinkingDirection]:
        """Генерация направлений мысли для новых участников"""

        # Проверяем, есть ли у пользователя уже решение для этой задачи
        existing_solution = await self.data_adapter.get_user_solution_for_challenge(
            challenge_id, user_id
        )

        if existing_solution:
            raise ValueError("Пользователь уже имеет решение для этой задачи")

        # Получаем задачу и существующие решения
        challenge = await self.data_adapter.get_challenge(challenge_id)
        if not challenge:
            raise ValueError("Задача не найдена")

        existing_solutions = await self.data_adapter.get_challenge_solutions(
            challenge_id)

        # Генерируем направления через LLM
        async with self.llm_service:
            directions = await self.llm_service.generate_thinking_directions(
                challenge, existing_solutions
            )

        return directions

    # === Запросы к коллективному интеллекту ===

    async def request_collective_ideas(
            self,
            solution_id: str,
            max_ideas: int = 3
    ) -> Dict[str, Any]:
        """Запрос новых идей от коллективного интеллекта"""

        # Получаем решение пользователя
        solution = await self.data_adapter.get_solution(solution_id)
        if not solution:
            raise ValueError("Решение не найдено")

        # Получаем другие решения для той же задачи
        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        if len(other_solutions) < 1:
            raise ValueError(
                "Недостаточно решений для анализа коллективного интеллекта")

        # Генерируем идеи через LLM
        async with self.llm_service:
            ideas = await self.llm_service.generate_collective_ideas(
                solution, other_solutions, max_ideas
            )

        # Создаем взаимодействие
        interaction = await self.data_adapter.create_collective_interaction(
            solution=solution,
            interaction_type="combinations"
        )

        # Создаем комбинации
        combinations_data = []
        for idea in ideas:
            combination_data = {
                "new_idea_description": idea.idea_description,
                "potential_impact": idea.potential_impact,
                "reasoning": idea.reasoning,
                "source_elements": []
            }

            # Создаем элементы источников на основе combination_elements
            for i, element in enumerate(idea.combination_elements):
                solution_id = element.get("solution_id")
                if solution_id == solution.id:
                    source_solution = solution
                else:
                    source_solution = await self.data_adapter.get_solution(
                        element.get("solution_id")
                    )
                source_element = {
                    "source_solution": source_solution,
                    "element_description": element.get("element"),
                    "element_context": element.get("reasoning"),
                }
                combination_data["source_elements"].append(source_element)

            combinations_data.append(combination_data)

        await self.data_adapter.create_interaction_combinations(
            interaction=interaction,
            combinations_data=combinations_data
        )
        await self.data_adapter.session.commit()

        return {
            "interaction_id": interaction.id,
            "ideas": ideas,
            "total_count": len(ideas)
        }

    async def request_improvement_suggestions(
            self,
            solution_id: str,
            max_suggestions: int = 4
    ) -> Dict[str, Any]:
        """Запрос предложений по улучшению решения"""

        solution = await self.data_adapter.get_solution(solution_id)
        if not solution:
            raise ValueError("Решение не найдено")

        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        if len(other_solutions) < 1:
            raise ValueError("Недостаточно решений для генерации предложений")

        # Генерируем предложения через LLM
        async with self.llm_service:
            suggestions = await self.llm_service.generate_improvement_suggestions(
                solution, other_solutions, max_suggestions
            )

        # Создаем взаимодействие
        interaction = await self.data_adapter.create_collective_interaction(
            solution=solution,
            interaction_type="suggestions"
        )

        # Создаем предложения
        suggestions_data = []
        for suggestion in suggestions:
            suggestion_data = {
                "element_description": suggestion.target_element,
                "integration_advice": suggestion.integration_advice,
                "source_solutions_count": len(suggestion.source_examples),
                "reasoning": suggestion.reasoning
            }
            suggestions_data.append(suggestion_data)

        await self.data_adapter.create_interaction_suggestions(
            interaction=interaction,
            suggestions_data=suggestions_data
        )
        await self.data_adapter.session.commit()

        return {
            "interaction_id": interaction.id,
            "suggestions": suggestions,
            "total_count": len(suggestions)
        }

    async def request_solution_criticism(
            self,
            solution_id: str,
            max_criticisms: int = 3
    ) -> Dict[str, Any]:
        """Запрос критики решения"""

        solution = await self.data_adapter.get_solution(solution_id)
        if not solution:
            raise ValueError("Решение не найдено")

        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        if len(other_solutions) < 1:
            raise ValueError("Недостаточно решений для генерации критики")

        # Генерируем критику через LLM
        async with self.llm_service:
            criticisms = await self.llm_service.generate_solution_criticism(
                solution, other_solutions, max_criticisms
            )

        # Создаем взаимодействие
        interaction = await self.data_adapter.create_collective_interaction(
            solution=solution,
            interaction_type="criticism"
        )

        # Создаем критику
        criticisms_data = []
        for criticism in criticisms:
            criticism_data = {
                "criticism_text": criticism.criticism_text,
                "severity": criticism.severity,
                "suggested_fix": criticism.suggested_fix,
                "reasoning": criticism.reasoning
            }
            criticisms_data.append(criticism_data)

        await self.data_adapter.create_interaction_criticisms(
            interaction=interaction,
            criticisms_data=criticisms_data
        )
        await self.data_adapter.session.commit()

        return {
            "interaction_id": interaction.id,
            "criticisms": criticisms,
            "total_count": len(criticisms)
        }

    # === Обработка ответов пользователя ===

    async def respond_to_interaction(
            self,
            interaction_id: str,
            item_responses: List[Dict[str, Any]]
    ) -> bool:
        """Обработка ответа пользователя на взаимодействие с ИИ"""

        # Обрабатываем ответы пользователя
        accepted_count = 0
        rejected_count = 0
        user_reasonings = []

        for item_response in item_responses:
            response_type = item_response.get("response")
            reasoning = item_response.get("reasoning")

            if response_type in ["accepted", "modified"]:
                accepted_count += 1
            elif response_type == "rejected":
                rejected_count += 1

            if reasoning:
                user_reasonings.append(reasoning)

        # Сохраняем ответ пользователя
        response_summary = (
            f"accepted:{accepted_count},rejected:{rejected_count}"
        )
        success = await self.data_adapter.update_interaction_response(
            interaction_id=interaction_id,
            user_response=response_summary,
            user_reasoning="; ".join(
                user_reasonings
            ) if user_reasonings else None
        )
        await self.data_adapter.session.commit()

        return success

    async def delete_interaction(self, interaction_id: str) -> None:
        await self.data_adapter.delete_interaction(interaction_id)
        await self.data_adapter.session.commit()

    async def delete_solution(self, solution_id: str) -> None:
        await self.data_adapter.delete_solution(solution_id)
        await self.data_adapter.session.commit()

    async def integrate_accepted_items(
            self,
            solution_id: str,
            interaction_id: str,
            accepted_items: List[Dict[str, Any]],
            user_modifications: Optional[List[str]] = None
    ) -> str:
        """Интеграция принятых предложений в решение"""

        solution = await self.data_adapter.get_solution(solution_id)
        if not solution:
            raise ValueError("Решение не найдено")

        # Генерируем интегрированную версию через LLM
        async with self.llm_service:
            integrated_text = await self.llm_service.integrate_accepted_items(
                solution, accepted_items, user_modifications
            )

        return integrated_text

    async def create_solution_version(
            self,
            solution_id: str,
            new_content: str,
            change_description: str,
            influenced_by_interactions: Optional[List[str]] = None
    ) -> bool:
        """Создание новой версии решения"""

        success = await self.data_adapter.create_solution_version(
            solution_id=solution_id,
            content=new_content,
            change_description=change_description,
            influenced_by_interactions=influenced_by_interactions
        )
        await self.data_adapter.session.commit()

        return success

    # === Аналитика и метрики ===

    async def get_solution_ai_influence(self, solution_id: str) -> Dict[
        str, Any]:
        """Получение метрик влияния ИИ на решение"""

        stats = await self.data_adapter.get_solution_statistics(solution_id)
        versions = await self.data_adapter.get_solution_versions(solution_id)

        # Подсчитываем AI взаимодействия из версий
        ai_interactions = 0
        for version in versions:
            # Получаем влияния для каждой версии
            # Это упрощенная версия, в реальности нужен отдельный метод
            ai_interactions += 1 if hasattr(version,
                                            'influences') and version.influences else 0

        return {
            "solution_id": solution_id,
            "total_versions": len(versions),
            "ai_interactions": ai_interactions,
            "collective_influence_percentage": stats.get(
                "collective_influence_percentage", 0),
            "ai_contribution_timeline": self._build_ai_timeline(versions)
        }

    async def get_collective_metrics(
            self,
            challenge_id: str
    ) -> Dict[str, Any]:
        """Получение метрик коллективного интеллекта для задачи"""

        analytics = await self.data_adapter.get_challenge_analytics(
            challenge_id)

        # Дополнительные метрики коллективного интеллекта
        return {
            **analytics,
            "ai_utilization_rate": 0,  # Процент пользователей, использующих ИИ
            "average_interactions_per_solution": 0,
            "most_effective_ai_suggestions": [],
            "collaboration_intensity": "medium"  # low, medium, high
        }

    async def get_community_ai_overview(
            self,
            community_id: str
    ) -> Dict[str, Any]:
        """Обзор использования ИИ в сообществе"""

        solutions = await self.data_adapter.get_community_solutions(
            community_id)

        total_solutions = len(solutions)
        ai_assisted_solutions = 0
        total_ai_interactions = 0

        for solution in solutions:
            stats = await self.data_adapter.get_solution_statistics(
                solution.id)
            if stats.get("total_interactions", 0) > 0:
                ai_assisted_solutions += 1
                total_ai_interactions += stats.get("total_interactions", 0)

        return {
            "community_id": community_id,
            "total_solutions": total_solutions,
            "ai_assisted_solutions": ai_assisted_solutions,
            "ai_adoption_rate": round(
                (ai_assisted_solutions / max(1, total_solutions)) * 100, 1),
            "total_ai_interactions": total_ai_interactions,
            "average_interactions_per_solution": round(
                total_ai_interactions / max(1, total_solutions), 1),
            "generated_at": datetime.now()
        }

    # === Вспомогательные методы ===

    def _build_ai_timeline(self, versions: List) -> List[Dict[str, Any]]:
        """Построение временной шкалы влияния ИИ"""
        timeline = []

        for version in versions:
            # Упрощенная проверка влияния ИИ
            # В реальности нужно проверять связи с VersionInteractionInfluence
            has_ai_influence = hasattr(version,
                                       'influences') and version.influences

            if has_ai_influence:
                timeline.append({
                    "version_number": version.version_number,
                    "created_at": version.created_at.isoformat() if version.created_at else None,
                    "ai_influences_count": len(
                        version.influences) if version.influences else 0,
                    "change_description": version.change_description
                })

        return timeline

    async def validate_solution_access(
            self,
            solution_id: str,
            user_id: str
    ) -> bool:
        """Проверка прав доступа к решению"""
        solution = await self.data_adapter.get_solution(solution_id)
        return solution is not None and solution.user_id == user_id

    async def get_pending_interactions(
            self,
            solution_id: str
    ) -> List[Dict[str, Any]]:
        """Получение ожидающих ответа взаимодействий с полными данными"""
        interactions = await self.data_adapter.get_pending_interactions(
            solution_id)

        detailed_interactions = []
        for interaction in interactions:
            # Получаем детальную информацию о взаимодействии
            interaction_details = await self.data_adapter.get_interaction_with_details(
                interaction.id
            )

            if interaction_details:
                formatted_interaction = {
                    "interaction_id": interaction.id,
                    "interaction_type": interaction.interaction_type,
                    "created_at": interaction.created_at.isoformat() if interaction.created_at else None,
                    "suggestions": [
                        {
                            "element_description": s.element_description,
                            "integration_advice": s.integration_advice,
                            "reasoning": s.reasoning
                        }
                        for s in interaction_details["suggestions"]
                    ],
                    "criticisms": [
                        {
                            "criticism_text": c.criticism_text,
                            "severity": c.severity,
                            "suggested_fix": c.suggested_fix,
                            "reasoning": c.reasoning
                        }
                        for c in interaction_details["criticisms"]
                    ],
                    "combinations": [
                        {
                            "new_idea_description": cb.new_idea_description,
                            "potential_impact": cb.potential_impact,
                            "reasoning": cb.reasoning
                        }
                        for cb in interaction_details["combinations"]
                    ]
                }
                detailed_interactions.append(formatted_interaction)

        return detailed_interactions
