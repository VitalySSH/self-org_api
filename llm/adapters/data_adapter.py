from typing import List, Optional, Dict, Any
from datetime import datetime

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.exceptions import CRUDNotFound
from datastorage.crud.interfaces.list import Filter, Operation, PaginationModel
from datastorage.database.models import (
    Challenge, Solution, CollectiveInteraction, SolutionVersion,
    InteractionSuggestion, InteractionCriticism, InteractionCombination,
    CombinationSourceElement, VersionInteractionInfluence
)
from entities.solution_preprocessing.model import SolutionPreprocessing


class DataAdapter:
    """Адаптер для работы с данными лаборатории через CRUDDataStorage"""

    def __init__(self, session=None):
        self.session = session

    async def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Получение задачи по ID"""
        ds = CRUDDataStorage(model=Challenge, session=self.session)
        async with ds.session_scope(read_only=True):
            return await ds.get(instance_id=challenge_id)

    async def get_challenge_solutions(self, challenge_id: str) -> List[
        Solution]:
        """Получение всех решений для задачи"""
        ds = CRUDDataStorage(model=Solution, session=self.session)
        async with ds.session_scope(read_only=True):
            filters = [
                Filter(
                    field="challenge_id",
                    op=Operation.EQ,
                    val=challenge_id,
                ),
                Filter(
                    field="current_content",
                    op=Operation.NOT_EQ,
                    val='',
                ),
            ]
            response = await ds.list(filters=filters)
            return response.data

    async def get_solution(self, solution_id: str) -> Optional[Solution]:
        """Получение решения по ID"""
        ds = CRUDDataStorage(model=Solution, session=self.session)
        async with ds.session_scope(read_only=True):
            return await ds.get(instance_id=solution_id)

    async def get_user_solution_for_challenge(
            self,
            challenge_id: str,
            user_id: str
    ) -> Optional[Solution]:
        """Получение решения пользователя для конкретной задачи"""
        ds = CRUDDataStorage(model=Solution, session=self.session)
        async with ds.session_scope(read_only=True):
            filters = [
                Filter(
                    field="challenge_id",
                    op=Operation.EQ,
                    val=challenge_id
                ),
                Filter(
                    field="user_id",
                    op=Operation.EQ,
                    val=user_id
                )
            ]
            return await ds.first(filters=filters)

    async def get_other_solutions_for_challenge(
            self,
            challenge_id: str,
            exclude_user_id: str
    ) -> List[Solution]:
        """Получение решений других участников для задачи"""
        ds = CRUDDataStorage(model=Solution, session=self.session)
        async with ds.session_scope(read_only=True):
            filters = [
                Filter(
                    field="challenge_id",
                    op=Operation.EQ,
                    val=challenge_id
                ),
                Filter(
                    field="user_id",
                    op=Operation.NOT_EQ,
                    val=exclude_user_id
                )
            ]
            response = await ds.list(filters=filters)
            return response.data

    async def create_collective_interaction(
            self,
            solution: Solution,
            interaction_type: str
    ) -> CollectiveInteraction:
        """Создание записи взаимодействия с ИИ"""
        ds = CRUDDataStorage(model=CollectiveInteraction, session=self.session)
        interaction = CollectiveInteraction()
        interaction.solution = solution
        interaction.interaction_type = interaction_type
        interaction.user_response = 'pending'
        interaction.applied_to_solution = False
        interaction.created_at = datetime.now()

        return await ds.create(instance=interaction)

    async def create_interaction_suggestions(
            self,
            interaction: CollectiveInteraction,
            suggestions_data: List[Dict[str, Any]]
    ) -> List[InteractionSuggestion]:
        """Создание предложений для взаимодействия"""
        ds = CRUDDataStorage(model=InteractionSuggestion, session=self.session)
        created_suggestions = []

        for suggestion_data in suggestions_data:
            suggestion = InteractionSuggestion()
            suggestion.interaction = interaction
            suggestion.element_description = suggestion_data.get(
                        "element_description"
            )
            suggestion.integration_advice = suggestion_data.get(
                        "integration_advice"
            )
            suggestion.source_solutions_count = suggestion_data.get(
                        "source_solutions_count"
            )
            suggestion.reasoning = suggestion_data.get("reasoning")
            created_suggestion = await ds.create(instance=suggestion)
            created_suggestions.append(created_suggestion)

        return created_suggestions

    async def create_interaction_criticisms(
            self,
            interaction: CollectiveInteraction,
            criticisms_data: List[Dict[str, Any]]
    ) -> List[InteractionCriticism]:
        """Создание критики для взаимодействия"""
        ds = CRUDDataStorage(model=InteractionCriticism, session=self.session)
        created_criticisms = []

        for criticism_data in criticisms_data:
            criticism = InteractionCriticism()
            criticism.interaction = interaction
            criticism.criticism_text = criticism_data.get("criticism_text")
            criticism.severity = criticism_data.get("severity")
            criticism.suggested_fix = criticism_data.get("suggested_fix")
            criticism.reasoning = criticism_data.get("reasoning")
            created_criticism = await ds.create(instance=criticism)
            created_criticisms.append(created_criticism)

        return created_criticisms

    async def create_interaction_combinations(
            self,
            interaction: CollectiveInteraction,
            combinations_data: List[Dict[str, Any]]
    ) -> List[InteractionCombination]:
        """Создание комбинаций для взаимодействия"""
        ds = CRUDDataStorage(
            model=InteractionCombination, session=self.session
        )
        created_combinations = []

        for combination_data in combinations_data:
            combination = InteractionCombination()
            combination.interaction = interaction
            combination.new_idea_description = (
                combination_data["new_idea_description"]
            )
            combination.potential_impact = (
                combination_data["potential_impact"]
            )
            combination.reasoning = combination_data["reasoning"]
            created_combination = await ds.create(instance=combination)

            # Создаем элементы источников
            for source_element in combination_data.get("source_elements", []):
                source_solution = source_element.get("source_solution")
                if not source_solution:
                    continue

                source = CombinationSourceElement()
                source.combination = created_combination
                source.source_solution = source_element.get(
                    "source_solution"
                )
                source.element_description = source_element.get(
                    "element_description"
                )
                source.element_context = source_element.get(
                    "element_context"
                )

                await ds.create(instance=source)

            created_combinations.append(created_combination)

        return created_combinations

    async def get_pending_interactions(
            self,
            solution_id: str
    ) -> List[CollectiveInteraction]:
        """Получение ожидающих ответа взаимодействий"""
        ds = CRUDDataStorage(model=CollectiveInteraction, session=self.session)
        async with ds.session_scope(read_only=True):
            filters = [
                Filter(
                    field="solution_id",
                    op=Operation.EQ,
                    val=solution_id
                ),
                Filter(
                    field="user_response",
                    op=Operation.EQ,
                    val="pending"
                )
            ]
            response = await ds.list(filters=filters)
            return response.data

    async def get_interaction_with_details(
            self,
            interaction_id: str
    ) -> Optional[Dict[str, Any]]:
        """Получение взаимодействия со всеми деталями"""
        ds = CRUDDataStorage(model=CollectiveInteraction, session=self.session)

        async with ds.session_scope(read_only=True):
            interaction = await ds.get(instance_id=interaction_id)
            if not interaction:
                return None

            result = {
                "interaction": interaction,
                "suggestions": [],
                "criticisms": [],
                "combinations": []
            }

            # Получаем связанные данные в зависимости от типа
            if interaction.interaction_type == "suggestions":
                filters = [
                    Filter(
                        field="interaction_id",
                        op=Operation.EQ,
                        val=interaction_id
                    )
                ]
                suggestions_response = await ds.list(
                    filters=filters,
                    model=InteractionSuggestion,
                )
                result["suggestions"] = suggestions_response.data

            elif interaction.interaction_type == "criticism":
                filters = [
                    Filter(
                        field="interaction_id",
                        op=Operation.EQ,
                        val=interaction_id
                    )
                ]
                criticisms_response = await ds.list(
                    filters=filters,
                    model=InteractionCriticism,
                )
                result["criticisms"] = criticisms_response.data

            elif interaction.interaction_type == "combinations":
                filters = [
                    Filter(
                        field="interaction_id",
                        op=Operation.EQ,
                        val=interaction_id
                    )
                ]
                combinations_response = await ds.list(
                    filters=filters,
                    model=InteractionCombination,
                )
                result["combinations"] = combinations_response.data

            return result

    async def update_interaction_response(
            self,
            interaction_id: str,
            user_response: str,
            user_reasoning: Optional[str] = None
    ) -> bool:
        """Обновление ответа пользователя на взаимодействие"""
        ds = CRUDDataStorage(model=CollectiveInteraction, session=self.session)
        try:
            interaction = await ds.get(instance_id=interaction_id)
            if not interaction:
                raise CRUDNotFound(
                    f"Interaction not found: {interaction_id}"
                )
            interaction.user_response = user_response
            interaction.user_reasoning = user_reasoning
            interaction.responded_at = datetime.now()
            if user_reasoning:
                interaction.user_reasoning = user_reasoning

            return True
        except Exception:
            return False

    async def delete_interaction(self, interaction_id: str) -> None:
        ds = CRUDDataStorage(model=CollectiveInteraction, session=self.session)
        interaction = await ds.get(
            instance_id=interaction_id,
            include=[
                "suggestions",
                "criticisms",
                "combinations.source_elements",
                "influences"
            ]
        )
        if not interaction:
            return

        for suggestion in interaction.suggestions:
            await self.session.delete(suggestion)

        for criticism in interaction.criticisms:
            await self.session.delete(criticism)

        for combination in interaction.combinations:
            for source_element in combination.source_elements:
                await self.session.delete(source_element)

            await self.session.delete(combination)

        for influence in interaction.influences:
            await self.session.delete(influence)

        await self.session.delete(interaction)

    async def delete_solution(self, solution_id: str) -> None:
        ds = CRUDDataStorage(model=Solution, session=self.session)
        solution = await ds.get(
            instance_id=solution_id,
            include=[
                "versions",
                "interactions.suggestions",
                "interactions.criticisms",
                "interactions.combinations.source_elements",
                "interactions.influences",
            ]
        )
        if not solution:
            return

        for interaction in solution.interactions:
            for suggestion in interaction.suggestions:
                await self.session.delete(suggestion)

            for criticism in interaction.criticisms:
                await self.session.delete(criticism)

            for combination in interaction.combinations:
                for source_element in combination.source_elements:
                    if source_element:
                        await self.session.delete(source_element)

                await self.session.delete(combination)

            for influence in interaction.influences:
                await self.session.delete(influence)


            await self.session.delete(interaction)

        for version in solution.versions:
            await self.session.delete(version)

        await self.session.delete(solution)

    async def get_solution_versions(self, solution_id: str) -> List[
        SolutionVersion]:
        """Получение версий решения"""
        ds = CRUDDataStorage(model=SolutionVersion, session=self.session)
        async with ds.session_scope(read_only=True):
            filters = [
                Filter(
                    field="solution_id",
                    op=Operation.EQ,
                    val=solution_id
                )
            ]
            response = await ds.list(filters=filters)
            return response.data

    async def create_solution_version(
            self,
            solution_id: str,
            content: str,
            change_description: str,
            influenced_by_interactions: Optional[List[str]] = None
    ) -> bool:
        """Создание новой версии решения"""
        ds = CRUDDataStorage(
            model=SolutionVersion, session=self.session
        )

        try:
            # Получаем текущие версии для определения номера
            existing_versions = await self.get_solution_versions(
                solution_id
            )
            solution = await ds.get(
                instance_id=solution_id, model=Solution
            )
            version_number = len(existing_versions) + 1

            # Создаем новую версию
            version = SolutionVersion()
            version.solution = solution
            version.content = content
            version.change_description = change_description
            version.version_number = version_number
            created_version = await ds.create(instance=version)

            # Обновляем основное решение
            solution.current_content = content
            solution.updated_at = datetime.now()

            # Создаем записи о влиянии взаимодействий
            if influenced_by_interactions:
                for interaction_id in influenced_by_interactions:
                    interaction = await ds.get(
                        instance_id=interaction_id,
                        model=CollectiveInteraction,
                    )
                    influence = VersionInteractionInfluence()
                    influence.solution_version = created_version
                    influence.collective_interaction = interaction
                    influence.influence_type = "direct"
                    influence.description = (
                        f"Влияние взаимодействия {interaction_id}"
                    )
                    await ds.create(instance=influence)

            return True
        except Exception as e:
            print(str(e))
            return False

    async def get_community_solutions(
            self,
            community_id: str,
            limit: int = 100
    ) -> List[Solution]:
        """Получение всех решений сообщества для анализа"""
        ds = CRUDDataStorage(model=Solution, session=self.session)
        async with ds.session_scope(read_only=True):
            # Фильтрация через связь с Challenge
            filters = [
                Filter(
                    field="challenge.community_id",
                    op=Operation.EQ,
                    val=community_id
                )
            ]
            response = await ds.list(
                filters=filters,
                pagination=PaginationModel(limit=limit, skip=1)
            )
            return response.data

    async def get_solution_statistics(self, solution_id: str) -> Dict[
        str, Any]:
        """Получение статистики по решению"""
        ds = CRUDDataStorage(model=Solution, session=self.session)

        async with ds.session_scope(read_only=True):
            solution = await ds.get(instance_id=solution_id)
            if not solution:
                return {}

            # Получаем взаимодействия
            interaction_filters = [
                Filter(
                    field="solution_id",
                    op=Operation.EQ,
                    val=solution_id
                )
            ]
            interactions_response = await ds.list(
                filters=interaction_filters,
                model=CollectiveInteraction,
            )
            interactions = interactions_response.data

            # Считаем статистику
            total_interactions = len(interactions)
            accepted_interactions = len([
                i for i in interactions
                if i.user_response in ["accepted", "modified"]
            ])

            versions = await self.get_solution_versions(solution_id)

            return {
                "solution_id": solution_id,
                "total_versions": len(versions),
                "total_interactions": total_interactions,
                "accepted_interactions": accepted_interactions,
                "collective_influence_percentage": (
                    (accepted_interactions / max(1, len(versions) - 1)) * 100
                    if len(versions) > 1 else 0
                ),
                "last_updated": solution.updated_at,
            }

    async def get_challenge_analytics(
            self,
            challenge_id: str,
    ) -> Dict[str, Any]:
        """Аналитика по задаче"""
        solutions = await self.get_challenge_solutions(challenge_id)

        if not solutions:
            return {
                "challenge_id": challenge_id,
                "total_solutions": 0,
                "unique_participants": 0,
                "average_collective_influence": 0
            }

        # Базовая статистика
        unique_users = len(set(s.user_id for s in solutions))

        # Считаем средний процент влияния ИИ
        influence_percentages = []
        for solution in solutions:
            stats = await self.get_solution_statistics(solution.id)
            influence_percentages.append(
                stats.get("collective_influence_percentage", 0)
            )

        avg_influence = sum(influence_percentages) / len(
            influence_percentages
        ) if influence_percentages else 0

        return {
            "challenge_id": challenge_id,
            "total_solutions": len(solutions),
            "unique_participants": unique_users,
            "average_collective_influence": round(avg_influence, 1),
            "solutions_with_ai_help": len(
                [p for p in influence_percentages if p > 0]
            ),
        }

    async def get_or_create_preprocessing(
            self,
            solution_id: str
    ) -> Optional[SolutionPreprocessing]:
        """Получение предобработки или None если не существует"""
        ds = CRUDDataStorage(model=SolutionPreprocessing, session=self.session)
        async with ds.session_scope(read_only=True):
            return await ds.first(
                filters=[Filter(field="solution_id", op=Operation.EQ,
                                val=solution_id)]
            )

    async def update_preprocessing(
            self,
            solution_id: str,
            **kwargs
    ) -> bool:
        """Обновление предобработки"""
        ds = CRUDDataStorage(model=SolutionPreprocessing, session=self.session)
        prep = await self.get_or_create_preprocessing(solution_id)
        if prep:
            for key, value in kwargs.items():
                if hasattr(prep, key):
                    setattr(prep, key, value)
            return True
        return False
