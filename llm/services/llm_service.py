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

        system_prompt = """Ты - аналитик коллективного интеллекта. Анализируй существующие решения и выделяй основные подходы к решению проблемы.

        Анализируй решения по их СУТИ, а не по форме. Учитывай:
        - Практические и теоретические подходы
        - Творческие и логические методы  
        - Технические и гуманитарные решения
        
        КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:
        1. Включай в результат ТОЛЬКО те подходы, которые поддерживаются как минимум 2+ участниками
        2. Названия подходов должны быть нейтральными и описательными, без оценочных суждений
        3. Стартовый текст должен быть структурным шаблоном с незавершенными разделами для развития
        4. Все текстовые поля в JSON должны использовать экранированные символы \n вместо фактических переносов строк.
        5. Включай в результат только те подходы, у которых participants_count больше 1
        
        Для каждого подхода создай стартовый шаблон решения как основу для развития, не более 500 слов.

        Верни результат строго в валидном формате JSON:
        {
          "directions": [
            {
              "title": "Краткое название подхода",
              "description": "Описание философии подхода",
              "key_approaches": ["подход1", "подход2"],
              "participants_count": число участников,
              "initial_solution_text": "Структурированный шаблон с разделами для заполнения",
              "example_excerpts": ["цитата1", "цитата2"]
            }
          ]
        }"""

        solutions_text = self._format_solutions_for_analysis(existing_solutions)

        prompt = f"""
            ЗАДАЧА: {challenge.title}
            ОПИСАНИЕ: {challenge.description}

            СУЩЕСТВУЮЩИЕ РЕШЕНИЯ УЧАСТНИКОВ:
            {solutions_text}

            Проанализируй решения и выдели {max_directions} основных подходов к решению этой задачи.

            Для каждого подхода:
            1. Найди участников (2+ человека) с похожими решениями
            2. Определи ключевые методы и философию БЕСПРИСТРАСТНО
            3. Создай структурный шаблон с разделами для развития, объединяющий лучшие идеи этого подхода
            4. Добавь репрезентативные примеры-цитаты из оригинальных решений
            
            Шаблон должен:
            - Содержать НАЧАЛА разделов, а не готовый текст
            - Быть основой для творческого развития
            - Сохранять нейтральный тон без оценок
            - Основаться на реальных решениях группы участников
            """

        # Выбираем провайдер (Together AI лучше для креативных задач на русском)
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

        system_prompt = """Ты - креативный синтезатор коллективного интеллекта. 
            Анализируешь решения и создаешь новые идеи, комбинируя "полезные элементы" из разных решений.

            Ищи полезные элементы любого типа:
            - Практические методы и техники
            - Творческие подходы и метафоры
            - Аналитические frameworks
            - Жизненный опыт и аналогии
            - Неожиданные инсайты и наблюдения

            Создавай разные типы идей:
            - Практичные и логичные комбинации
            - Неожиданные, но обоснованные синтезы
            
            КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
            1. Описание идеи должно содержать 2-3 предложения, излагающих ТОЛЬКО суть идеи
            2. Строго запрещено создавать идеи, не основанные на конкретных "полезных элементах" из решений

            Верни результат строго в формате JSON:
            {
              "ideas": [
                {
                  "idea_description": "Описание новой идеи-комбинации",
                  "combination_elements": [
                    {
                      "element": "конкретный элемент или подход",
                      "solution_id": "uuid решения",
                      "reasoning": "почему этот элемент был выбран"
                    }
                  ],
                  "source_solutions_count": количество_источников,
                  "potential_impact": "Как это улучшит решение",
                  "reasoning": "Логика создания комбинации"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_detailed_analysis(
            other_solutions
        )

        prompt = f"""
            АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}

            ДРУГИЕ РЕШЕНИЯ ДЛЯ КОМБИНИРОВАНИЯ:
            {other_solutions_text}

            Создай {max_ideas} новые идеи, комбинируя элементы из разных решений:

            1. Разложи каждое решение на "полезные элементы" (методы, аналогии, инсайты, подходы)
            2. Найди интересные комбинации элементов из РАЗНЫХ решений
            3. Убедись, что комбинации НЕ присутствуют в анализируемом решении
            4. Каждая идея должна использовать элементы минимум из 2 разных решений
            5. Идеи должны быть логически обоснованными
            6. Создавай разные типы идей: как практичные, так и неожиданные

            НЕ предлагай то, что уже есть в анализируемом решении!
            """

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

        system_prompt = """Ты - консультант по улучшению решений. 
            Анализируешь решение и предлагаешь конкретные улучшения на основе опыта других участников.

            Верни результат строго в формате JSON:
            {
              "suggestions": [
                {
                  "target_element": "Какой элемент решения улучшить",
                  "improvement_description": "Конкретное предложение по улучшению",
                  "integration_advice": "Как интегрировать в решение",
                  "source_examples": ["пример1 из другого решения", "пример2"],
                  "reasoning": "Почему это улучшение полезно"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_analysis(other_solutions)

        prompt = f"""
            АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}

            РЕШЕНИЯ ДРУГИХ УЧАСТНИКОВ:
            {other_solutions_text}

            Предложи {max_suggestions} конкретных улучшений для анализируемого решения:

            1. Найди элементы решения, которые можно усилить
            2. Найди в других решениях успешные подходы к похожим элементам
            3. Предложи конкретные способы улучшения
            
            ВАЖНЫЕ ТРЕБОВАНИЯ К ПРИМЕРАМ:
            - В source_examples приводи ТОЧНЫЕ идеи из решений в виде 2-3 предложений
            - Примеры должны быть ОБЕЗЛИЧЕНЫ: не упоминай номера решений, авторов или идентификаторы
            - Каждый пример должен конкретно описывать подход или метод из реального решения
            - Избегай общих фраз, фокусируйся на конкретных деталях из текстов решений

            Фокусируйся на:
            - Практичных, применимых предложениях для данной задачи
            - Конкретных элементах, а не общих рекомендациях  
            - Примерах из реальных решений других участников
            - Улучшениях, релевантных типу задачи
            """

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

        system_prompt = """Ты - критический аналитик решений. 
            Находишь потенциальные слабые места и проблемы в решении на основе сравнения с другими подходами.

            Верни результат строго в формате JSON:
            {
              "criticisms": [
                {
                  "criticism_text": "Конкретная критика или проблема",
                  "severity": "minor|major|critical",
                  "evidence": ["доказательство1 из других решений", "доказательство2"],
                  "suggested_fix": "Как можно исправить проблему",
                  "reasoning": "Обоснование критики"
                }
              ]
            }"""

        other_solutions_text = self._format_solutions_for_analysis(other_solutions)

        prompt = f"""
            АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}

            ДРУГИЕ РЕШЕНИЯ ДЛЯ СРАВНЕНИЯ:
            {other_solutions_text}

            Найди {max_criticisms} обоснованных критических замечаний:

            1. Сравни решение с альтернативными подходами
            2. Найди потенциальные слабые места или упущения
            3. Для каждой критики предложи способ исправления
            4. Используй примеры из других решений как доказательство
            
            ВАЖНЫЕ ТРЕБОВАНИЯ:
            - В reasoning используй ОБЕЗЛИЧЕННЫЕ формулировки: описывай подходы, а не конкретные решения
            - Не упоминай номера решений, авторов или идентификаторы в reasoning
            - Фокусируйся на методологических различиях и альтернативных подходах
            - Критика должна быть направлена на конкретные элементы анализируемого решения

            Критика должна быть:
            - Конструктивной (с предложением исправления)
            - Обоснованной (с примерами из других решений)
            - Конкретной (не общие фразы)

            НЕ критикуй стиль изложения - только содержательные аспекты!
            """

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

        system_prompt = """Ты - редактор решений. Помогаешь аккуратно интегрировать принятые предложения в существующее решение.

        Создай улучшенную версию решения, которая:
        1. Сохраняет авторский стиль и структуру
        2. Логично интегрирует принятые предложения только в нужные места
        3. Обеспечивает связность и читаемость текста
        4. Не изменяет неизмененные части текста
        """

        items_text = self._format_accepted_items(
            accepted_items, user_modifications
        )

        prompt = f"""
            ТЕКУЩЕЕ РЕШЕНИЕ:
            {current_solution.current_content}

            ПРИНЯТЫЕ ПРЕДЛОЖЕНИЯ ДЛЯ ИНТЕГРАЦИИ:
            {items_text}

            АККУРАТНО интегрируй предложения в существующее решение:
            
            СТРОГИЕ ОГРАНИЧЕНИЯ:
            1. ЗАПРЕЩЕНО изменять текст в разделах, не связанных с принятыми предложениями
            2. ЗАПРЕЩЕНО переписывать оригинальные формулировки без необходимости
            3. ЗАПРЕЩЕНО менять структуру текста, кроме целевых мест интеграции
            4. Разрешается изменять ТОЛЬКО те части текста, которые непосредственно связаны с предложениями
            
            ВАЖНЫЕ ПРАВИЛА РЕДАКТИРОВАНИЯ:
            1. Сохраняй оригинальную структуру текста - не переписывай полностью
            2. Вноси изменения ТОЛЬКО в те разделы, которые затрагиваются предложениями
            3. При интеграции новых идей старайся использовать стиль и лексику автора
            6. Избегай полного переписывания текста - только точечные улучшения
            
            ЦЕЛЬ: Пользователь должен видеть, что это то же самое решение, но улучшенное, а не полностью новый текст.
            
            Ограничение: объём текста не должен превышать 3000 символов.
            
            Финальный текст должен сохранять узнаваемость оригинала при интеграции улучшений.
            """

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

        if provider.name == "groq":
            return await self._call_openai_compatible(
                provider, prompt, system_prompt, response_format
            )
        elif provider.name == "together":
            return await self._call_openai_compatible(
                provider, prompt, system_prompt, response_format
            )
        elif provider.name == "huggingface":
            return await self._call_huggingface(
                provider, prompt, system_prompt, response_format
            )
        else:
            raise ValueError(f"Unknown provider: {provider.name}")

    async def _call_openai_compatible(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str,
    ) -> Dict[str, Any]:
        """Вызов OpenAI-совместимых API (Groq, Together AI)"""

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        token_info = self.token_calc.calculate_optimal_max_tokens(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=prompt,
            safety_margin=0.15
        )

        if not token_info["fits_in_context"]:
            raise ValueError(
                f"Контекст слишком большой для провайдера {provider.name}. "
                f"Требуется: {token_info['context_tokens_with_margin']} токенов, "
                f"доступно: {token_info['provider_max_context']} токенов. "
                f"Попробуйте сократить количество анализируемых решений."
            )

        optimal_max_tokens = token_info["max_tokens"]

        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": optimal_max_tokens,
            "temperature": provider.temperature
        }

        async with self.session.post(
                provider.api_url,
                json=payload,
                headers=headers,
                timeout=provider.timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
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
            response_format: str,
    ) -> Dict[str, Any]:
        """Вызов Hugging Face API с динамическим расчётом токенов"""

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        full_prompt = (
            f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt
            else f"User: {prompt}\nAssistant:"
        )

        token_info = self.token_calc.calculate_optimal_max_tokens(
            provider=provider,
            system_prompt=system_prompt,
            user_prompt=prompt,
            safety_margin=0.15
        )

        if not token_info["fits_in_context"]:
            raise ValueError(
                f"Контекст слишком большой для провайдера {provider.name}. "
                f"Требуется: {token_info['context_tokens_with_margin']} токенов, "
                f"доступно: {token_info['provider_max_context']} токенов."
            )

        optimal_max_tokens = token_info["max_tokens"]

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": optimal_max_tokens,
                "temperature": provider.temperature,
                "return_full_text": False,
                "do_sample": True
            }
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
