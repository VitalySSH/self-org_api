import json
from typing import List, Dict, Any, Optional
import aiohttp

from datastorage.database.models import Challenge, Solution
from .text_optimizer import TextOptimizer
from .token_calculator_service import get_token_calculator
from llm.models.lab import (
    LLMProvider, ThinkingDirection, ImprovementSuggestion,
    CriticismPoint, CollectiveIdea
)


class LLMService:

    def __init__(self, providers: List[LLMProvider]):
        self.providers = sorted(providers, key=lambda x: x.priority)
        self.providers_dict = {p.name: p for p in providers}
        self.session: Optional[aiohttp.ClientSession] = None
        self.token_calc = get_token_calculator()
        self._text_optimizer = TextOptimizer()

        self.groq_requests_count = 0
        self.groq_last_reset = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate_thinking_directions(
            self,
            challenge: Challenge,
            existing_solutions: List[Solution],
            max_directions: int = 5,
            preferred_provider: str = None
    ) -> List[ThinkingDirection]:
        """Генерация направлений мысли"""

        if len(existing_solutions) < 3:
            return []

        system_prompt = """Ты голос коллективного интеллекта. Анализируй решения по СУТИ, выделяй общие подходы группы.

            КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
            1. Включай ТОЛЬКО подходы с 2+ участниками (participants_count > 1)
            2. Названия подходов - нейтральные, без оценок
            3. initial_solution_text - структурный шаблон с незавершенными разделами (до 500 слов)
            4. В JSON используй \\n вместо реальных переносов строк
            
            КРИТИЧЕСКИЙ ЗАПРЕТ:
            - ЗАПРЕЩЕНО писать "решение #X", "участник Y"
            - Пиши обезличенно: "этот подход предполагает...", "участники данного направления..."
            
            ОТВЕТ - ТОЛЬКО валидный JSON, начиная с { и заканчивая }:
            {
              "directions": [
                {
                  "title": "string",
                  "description": "string",
                  "key_approaches": ["string"],
                  "participants_count": number,
                  "initial_solution_text": "string",
                  "example_excerpts": ["string"]
                }
              ]
            }"""

        solutions_text = self._format_solutions_for_analysis(existing_solutions)

        prompt = f"""ЗАДАЧА: {challenge.title}
            ОПИСАНИЕ: {challenge.description}
            
            РЕШЕНИЯ УЧАСТНИКОВ:
            {solutions_text}
            
            Выдели {max_directions} основных подходов. Для каждого:
            1. Найди 2+ участников с похожими решениями
            2. Определи ключевые методы БЕСПРИСТРАСТНО
            3. Создай шаблон с незавершенными разделами, объединяющий лучшие идеи
            4. Добавь краткие цитаты-примеры
            
            Шаблон должен быть ОСНОВОЙ для развития, не готовым текстом."""

        provider_name = preferred_provider or "together"
        response = await self._make_llm_request(
            prompt, system_prompt, "json", provider_name
        )
        return self._parse_directions_response(response)

    async def generate_collective_ideas(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_ideas: int = 3,
            preferred_provider: str = None
    ) -> List[CollectiveIdea]:
        """Генерация новых идей-комбинаций элементов"""

        system_prompt = """Ты креативный голос коллективного интеллекта. Комбинируй полезные элементы из общего опыта участников.

            Элементы: методы, техники, подходы, метафоры, опыт, инсайты, наблюдения.
            
            КРИТИЧЕСКИЙ ЗАПРЕТ:
            - ЗАПРЕЩЕНО писать "из решения #X", "участник Y предложил"
            - РАЗРЕШЕНО в combination_elements указывать solution_id (это техническое поле)
            - РАЗРЕШЕНО в описаниях: "один из методов", "некоторые участники"
            
            ТРЕБОВАНИЯ:
            1. idea_description - 2-3 предложения, ТОЛЬКО суть идеи, БЕЗ ссылок на решения
            2. Строго запрещены идеи БЕЗ конкретных элементов из решений
            
            ОТВЕТ - ТОЛЬКО JSON от { до }:
            {
              "ideas": [
                {
                  "idea_description": "string",
                  "combination_elements": [
                    {
                      "element": "string",
                      "solution_id": "uuid",
                      "reasoning": "string"
                    }
                  ],
                  "source_solutions_count": number,
                  "potential_impact": "string",
                  "reasoning": "string"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_detailed_analysis(
            other_solutions
        )

        prompt = f"""АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}
            
            ДРУГИЕ РЕШЕНИЯ:
            {other_solutions_text}
            
            Создай {max_ideas} новые идеи:
            1. Разложи решения на полезные элементы
            2. Найди интересные комбинации из РАЗНЫХ решений (минимум 2)
            3. Убедись, что комбинаций НЕТ в анализируемом решении
            4. Обоснуй каждую идею
            5. Создавай как практичные, так и неожиданные идеи"""

        provider_name = preferred_provider or "together"
        response = await self._make_llm_request(
            prompt, system_prompt, "json", provider_name
        )
        return self._parse_ideas_response(response)

    async def generate_improvement_suggestions(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_suggestions: int = 4,
            preferred_provider: str = None,
    ) -> List[ImprovementSuggestion]:
        """Генерация предложений по улучшению решения"""

        system_prompt = """Ты голос коллективного интеллекта. Анализируй решение и предлагай улучшения из общего опыта участников.

            КРИТИЧЕСКИЙ ЗАПРЕТ:
            - ЗАПРЕЩЕНО упоминать номера решений (#1, #3, "решение 5")
            - ЗАПРЕЩЕНО упоминать авторов или ID
            - ЗАПРЕЩЕНО писать "как в решении...", "согласно решению..."
            - РАЗРЕШЕНО: приводить краткие анонимные цитаты-примеры
            
            ТРЕБОВАНИЯ к improvement_description:
            - 2-3 предложения, ТОЛЬКО суть улучшения, БЕЗ ссылок на решения
            
            ТРЕБОВАНИЯ К source_examples:
            - ТОЧНЫЕ идеи из решений, 2-3 предложения
            - ПОЛНОСТЬЮ ОБЕЗЛИЧЕНЫ: пиши "один из подходов предлагает...", "некоторые участники используют..."
            - Конкретные методы, не общие фразы
            
            ОТВЕТ - ТОЛЬКО JSON от { до }:
            {
              "suggestions": [
                {
                  "target_element": "string",
                  "improvement_description": "string",
                  "integration_advice": "string",
                  "source_examples": ["string"],
                  "reasoning": "string"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_analysis(other_solutions)

        prompt = f"""АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}
            
            РЕШЕНИЯ ДРУГИХ:
            {other_solutions_text}
            
            Предложи {max_suggestions} конкретных улучшений:
            1. Найди элементы для усиления
            2. Найди успешные подходы в других решениях
            3. Предложи конкретные способы улучшения
            
            Фокус на: практичности, конкретике, примерах из реальных решений, релевантности задаче.
            
            ВАЖНО: В source_examples НЕ пиши "Решение #X" или "как в решении". Пиши только суть метода анонимно."""

        provider_name = preferred_provider or "together"
        response = await self._make_llm_request(
            prompt, system_prompt, "json", provider_name
        )
        return self._parse_suggestions_response(response)

    async def generate_solution_criticism(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_criticisms: int = 3,
            preferred_provider: str = None
    ) -> List[CriticismPoint]:
        """Генерация конструктивной критики решения"""

        system_prompt = """Ты голос коллективного критического мышления. Находишь слабые места через сравнение с альтернативными подходами коллектива.

            КРИТИЧЕСКИЙ ЗАПРЕТ:
            - ЗАПРЕЩЕНО упоминать номера решений (#1, "решение 3")
            - ЗАПРЕЩЕНО писать "в решении X", "автор решения Y"
            - РАЗРЕШЕНО: "альтернативный подход предполагает...", "некоторые участники используют..."
            
            ТРЕБОВАНИЯ К reasoning и evidence:
            - ПОЛНОСТЬЮ ОБЕЗЛИЧЕНЫ: без ссылок на конкретные решения
            - Фокус на методологических различиях подходов
            - Описывай подходы, а не решения
            
            ОТВЕТ - ТОЛЬКО JSON от { до }:
            {
              "criticisms": [
                {
                  "criticism_text": "string",
                  "severity": "minor|major|critical",
                  "evidence": ["string"],
                  "suggested_fix": "string",
                  "reasoning": "string"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_analysis(other_solutions)

        prompt = f"""АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}
            
            ДРУГИЕ РЕШЕНИЯ:
            {other_solutions_text}
            
            Найди {max_criticisms} обоснованных критических замечаний:
            1. Сравни с альтернативными подходами
            2. Найди слабые места или упущения
            3. Предложи способ исправления
            4. Используй примеры как доказательство
            
            Критика: конструктивная, обоснованная, конкретная. НЕ критикуй стиль - только содержание!"""

        provider_name = preferred_provider or "together"
        response = await self._make_llm_request(
            prompt, system_prompt, "json", provider_name
        )
        return self._parse_criticism_response(response)

    async def integrate_accepted_items(
            self,
            current_solution: Solution,
            accepted_items: List[Dict[str, Any]],
            user_modifications: Optional[List[str]] = None
    ) -> str:
        """Интеграция принятых предложений в решение"""

        system_prompt = """Ты редактор решений. Аккуратно интегрируй принятые предложения, сохраняя авторский стиль и структуру.

            ПРАВИЛА:
            1. Сохраняй стиль, структуру, оригинальные формулировки
            2. Изменяй ТОЛЬКО части, связанные с предложениями
            3. НЕ переписывай весь текст - только точечные улучшения
            4. Результат должен быть узнаваем как то же решение, но улучшенное"""

        items_text = self._format_accepted_items(
            accepted_items, user_modifications
        )

        prompt = f"""ТЕКУЩЕЕ РЕШЕНИЕ:
            {current_solution.current_content}
            
            ПРИНЯТЫЕ ПРЕДЛОЖЕНИЯ:
            {items_text}
            
            Аккуратно интегрируй предложения.
            
            ЗАПРЕЩЕНО:
            - Изменять текст вне связи с предложениями
            - Переписывать оригинальные формулировки без необходимости
            - Менять структуру вне целевых мест
            - Превышать 3000 символов
            
            РАЗРЕШЕНО: Изменять ТОЛЬКО части, связанные с предложениями.
            
            ЦЕЛЬ: То же решение, но улучшенное. Узнаваемый оригинал + точечные улучшения."""

        response = await self._make_llm_request(
            prompt, system_prompt, "text", "together"
        )
        return response.get("text", "")

    # === Вспомогательные методы ===

    async def _make_llm_request(
            self,
            prompt: str,
            system_prompt: str = "",
            response_format: str = "text",
            preferred_provider: str = None
    ) -> Dict[str, Any]:
        """Выполнение запроса к LLM с fallback"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        # Если указан preferred_provider, пробуем его первым
        providers = list(self.providers)
        if preferred_provider and preferred_provider in self.providers_dict:
            pref = self.providers_dict[preferred_provider]
            providers = [pref] + [p for p in providers if
                                  p.name != preferred_provider]

        last_error = None

        for provider in providers:
            try:
                response = await self._call_provider(
                    provider, prompt, system_prompt, response_format
                )
                if response:
                    return response
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name} model {provider.model} failed: {e}")
                continue

        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    async def _call_provider(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str
    ) -> Dict[str, Any]:
        """Вызов конкретного провайдера"""

        if "together" in provider.name or "groq" in provider.name:
            return await self._call_openai_compatible(
                provider, prompt, system_prompt, response_format
            )
        elif "huggingface" in provider.name:
            return await self._call_huggingface(
                provider, prompt, system_prompt, response_format
            )
        else:
            raise ValueError(f"Unknown provider type: {provider.name}")

    async def _call_openai_compatible(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str
    ) -> Dict[str, Any]:
        """Вызов OpenAI-совместимого API (Together, Groq)"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": provider.temperature,
            "max_tokens": provider.max_tokens
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        async with self.session.post(
                provider.api_url,
                json=payload,
                headers=headers,
                timeout=provider.timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = self._extract_text(data, provider.name)
                return self._parse_response(content, response_format)
            else:
                error_text = await response.text()
                raise Exception(
                    f"{provider.name} API error {response.status}: {error_text}"
                )

    async def _call_huggingface(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str
    ) -> Dict[str, Any]:
        """Вызов HuggingFace API"""

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": provider.max_tokens,
                "temperature": provider.temperature,
                "return_full_text": False
            }
        }

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        async with self.session.post(
                provider.api_url,
                json=payload,
                headers=headers,
                timeout=provider.timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    content = data.get("generated_text", data.get("text", ""))
                else:
                    content = str(data)
                return self._parse_response(content, response_format)
            else:
                error_text = await response.text()
                raise Exception(
                    f"Hugging Face API error {response.status}: {error_text}"
                )

    @staticmethod
    def _parse_response(content: str, response_format: str) -> Dict[str, Any]:
        """Парсинг ответа LLM"""
        if response_format == "json":
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
                else:
                    return json.loads(content)
            except json.JSONDecodeError:
                return {"text": content, "error": "Failed to parse as JSON"}
        else:
            return {"text": content}

    def _format_solutions_for_analysis(self, solutions: List[Solution]) -> str:
        """Форматирование решений для анализа с оптимизацией."""
        if not solutions:
            return "Нет доступных решений для анализа."

        formatted = []
        for i, solution in enumerate(solutions, 1):
            content = self._text_optimizer.clean_and_optimize(solution.current_content)

            formatted.append(f"""
                РЕШЕНИЕ #{i} (Автор: {solution.user_id[:8]}):
                {content}
                ---""")

        return "\n".join(formatted)

    def _format_solutions_for_detailed_analysis(self, solutions: List[Solution]) -> str:
        """Детальное форматирование для комбинирования с оптимизацией."""
        if not solutions:
            return "Нет доступных решений."

        formatted = []
        for i, solution in enumerate(solutions, 1):
            content = self._text_optimizer.clean_and_optimize(solution.current_content)

            formatted.append(f"""
                РЕШЕНИЕ #{i} (solution_id: {solution.id}):
                {content}
                ===================""")

        return "\n".join(formatted)

    @staticmethod
    def _format_accepted_items(
            accepted_items: List[Dict[str, Any]],
            user_modifications: Optional[List[str]] = None
    ) -> str:
        """Форматирование принятых предложений"""
        formatted = []
        for i, item in enumerate(accepted_items):
            text = f"ПРЕДЛОЖЕНИЕ {i + 1}: {item.get('text', 'Нет текста')}"
            if user_modifications and i < len(user_modifications):
                text += f"\nМОДИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ: {user_modifications[i]}"
            formatted.append(text)

        return "\n\n".join(formatted)

    # === Парсинг ответов LLM ===

    @staticmethod
    def _parse_directions_response(response: Dict[str, Any]) -> List[
        ThinkingDirection]:
        """Парсинг ответа для направлений мысли"""
        try:
            directions_data = response.get("directions", [])
            directions = []

            for direction_data in directions_data:
                direction = ThinkingDirection(
                    title=direction_data.get("title",
                                             "Неизвестное направление"),
                    description=direction_data.get("description", ""),
                    key_approaches=direction_data.get("key_approaches", []),
                    participants_count=direction_data.get("participants_count",
                                                          1),
                    initial_solution_text=direction_data.get(
                        "initial_solution_text", ""),
                    example_excerpts=direction_data.get("example_excerpts", [])
                )
                directions.append(direction)

            return directions
        except Exception:
            return []

    @staticmethod
    def _parse_ideas_response(
            response: Dict[str, Any]
    ) -> List[CollectiveIdea]:
        """Парсинг ответа для идей"""
        try:
            ideas_data = response.get("ideas", [])
            ideas = []

            for idea_data in ideas_data:
                idea = CollectiveIdea(
                    idea_description=idea_data.get("idea_description", ""),
                    combination_elements=idea_data.get("combination_elements",
                                                       []),
                    source_solutions_count=idea_data.get(
                        "source_solutions_count", 0),
                    potential_impact=idea_data.get("potential_impact", ""),
                    reasoning=idea_data.get("reasoning", "")
                )
                ideas.append(idea)

            return ideas
        except Exception:
            return []

    @staticmethod
    def _parse_suggestions_response(response: Dict[str, Any]) -> List[
        ImprovementSuggestion]:
        """Парсинг ответа для предложений по улучшению"""
        try:
            suggestions_data = response.get("suggestions", [])
            suggestions = []

            for suggestion_data in suggestions_data:
                suggestion = ImprovementSuggestion(
                    target_element=suggestion_data.get("target_element", ""),
                    improvement_description=suggestion_data.get(
                        "improvement_description", ""),
                    integration_advice=suggestion_data.get(
                        "integration_advice", ""),
                    source_examples=suggestion_data.get("source_examples", []),
                    reasoning=suggestion_data.get("reasoning", "")
                )
                suggestions.append(suggestion)

            return suggestions
        except Exception:
            return []

    @staticmethod
    def _parse_criticism_response(response: Dict[str, Any]) -> List[
        CriticismPoint]:
        """Парсинг ответа для критики"""
        try:
            criticisms_data = response.get("criticisms", [])
            criticisms = []

            for criticism_data in criticisms_data:
                criticism = CriticismPoint(
                    criticism_text=criticism_data.get("criticism_text", ""),
                    severity=criticism_data.get("severity", "minor"),
                    evidence=criticism_data.get("evidence", []),
                    suggested_fix=criticism_data.get("suggested_fix", ""),
                    reasoning=criticism_data.get("reasoning", "")
                )
                criticisms.append(criticism)

            return criticisms
        except Exception:
            return []

    @staticmethod
    def _extract_text(result: dict, provider_name: str) -> str:
        """Извлечение текста из ответа провайдера"""
        # Together AI, Groq, и другие OpenAI-совместимые
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "text" in choice:
                return choice["text"].strip()
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()

        # HuggingFace
        if isinstance(result, list) and len(result) > 0:
            if "generated_text" in result[0]:
                return result[0]["generated_text"].strip()

        raise ValueError(f"Неожиданный формат ответа от {provider_name}: {result}")
