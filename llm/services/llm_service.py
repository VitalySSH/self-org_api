import json
import hashlib
from typing import List, Dict, Any, Optional
import aiohttp

from datastorage.database.models import Challenge, Solution
from llm.models.lab import (
    LLMProvider, ThinkingDirection, ImprovementSuggestion,
    CriticismPoint, CollectiveIdea
)


class LLMService:
    """Переработанный LLM сервис для модуля лаборатории"""

    def __init__(self, providers: List[LLMProvider]):
        self.providers = sorted(providers, key=lambda x: x.priority)
        self.session: Optional[aiohttp.ClientSession] = None

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
            max_directions: int = 5
    ) -> List[ThinkingDirection]:
        """Генерация направлений мысли с готовыми стартовыми решениями"""

        if len(existing_solutions) < 3:
            return []  # Недостаточно данных для анализа

        system_prompt = """Ты - аналитик коллективного интеллекта. Анализируй существующие решения и выделяй основные подходы к решению проблемы.

        Анализируй решения по их СУТИ, а не по форме. Учитывай:
        - Практические и теоретические подходы
        - Творческие и логические методы  
        - Технические и гуманитарные решения

        Для каждого подхода создай готовый стартовый текст решения (300-500 слов), который новый участник может использовать как отправную точку.
        
        Верни результат строго в формате JSON:
        {
          "directions": [
            {
              "title": "Краткое название подхода",
              "description": "Описание философии подхода",
              "key_approaches": ["подход1", "подход2"],
              "participants_count": число_участников,
              "initial_solution_text": "Готовый стартовый текст решения для новичка",
              "example_excerpts": ["цитата1", "цитата2"]
            }
          ]
        }"""

        solutions_text = self._format_solutions_for_analysis(
            existing_solutions)

        prompt = f"""
            ЗАДАЧА: {challenge.title}
            ОПИСАНИЕ: {challenge.description}
            
            СУЩЕСТВУЮЩИЕ РЕШЕНИЯ УЧАСТНИКОВ:
            {solutions_text}
            
            Проанализируй решения и выдели {max_directions} основных подходов к решению этой задачи.
            
            Для каждого подхода:
            1. Найди участников с похожими решениями
            2. Определи ключевые методы и философию
            3. Создай готовый стартовый текст (300-500 слов), объединяющий лучшие идеи этого подхода
            4. Добавь примеры-цитаты из оригинальных решений
            
            Стартовый текст должен быть:
            - Структурированным и понятным
            - Основанным на реальных решениях участников
            - Готовым для использования новичком
            - Оставляющим пространство для творческого развития
            """

        response = await self._make_llm_request(prompt, system_prompt, "json")
        return self._parse_directions_response(response)

    async def generate_collective_ideas(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_ideas: int = 3
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

        response = await self._make_llm_request(prompt, system_prompt, "json")
        return self._parse_ideas_response(response)

    async def generate_improvement_suggestions(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_suggestions: int = 4
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

        other_solutions_text = self._format_solutions_for_analysis(
            other_solutions
        )

        prompt = f"""
            АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}
            
            РЕШЕНИЯ ДРУГИХ УЧАСТНИКОВ:
            {other_solutions_text}
            
            Предложи {max_suggestions} конкретных улучшения для анализируемого решения:
            
            1. Найди элементы решения, которые можно усилить
            2. Найди в других решениях успешные подходы к похожим элементам
            3. Предложи конкретные способы улучшения
            
            Фокусируйся на:
            - Практических, применимых предложениях для данной задачи
            - Конкретных элементах, а не общих рекомендациях  
            - Примерах из реальных решений других участников
            - Улучшениях, релевантных типу задачи
            """

        response = await self._make_llm_request(
            prompt, system_prompt, "json"
        )
        return self._parse_suggestions_response(response)

    async def generate_solution_criticism(
            self,
            target_solution: Solution,
            other_solutions: List[Solution],
            max_criticisms: int = 3
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

        other_solutions_text = self._format_solutions_for_analysis(
            other_solutions)

        prompt = f"""
            АНАЛИЗИРУЕМОЕ РЕШЕНИЕ:
            {target_solution.current_content}
            
            ДРУГИЕ РЕШЕНИЯ ДЛЯ СРАВНЕНИЯ:
            {other_solutions_text}
            
            Найди {max_criticisms} обоснованных критических замечания:
            
            1. Сравни решение с альтернативными подходами
            2. Найди потенциальные слабые места или упущения
            3. Для каждой критики предложи способ исправления
            4. Используй примеры из других решений как доказательство
            
            Критика должна быть:
            - Конструктивной (с предложением исправления)
            - Обоснованной (с примерами из других решений)
            - Конкретной (не общие фразы)
            
            НЕ критикуй стиль изложения - только содержательные аспекты!
            """

        response = await self._make_llm_request(
            prompt, system_prompt, "json"
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
        2. Логично интегрирует принятые предложения
        3. Обеспечивает связность и читаемость текста
        4. Выделяет изменения маркерами [ДОБАВЛЕНО: ...] или [ИЗМЕНЕНО: ...]"""

        items_text = self._format_accepted_items(accepted_items,
                                                 user_modifications)

        prompt = f"""
            ТЕКУЩЕЕ РЕШЕНИЕ:
            {current_solution.current_content}
            
            ПРИНЯТЫЕ ПРЕДЛОЖЕНИЯ ДЛЯ ИНТЕГРАЦИИ:
            {items_text}
            
            Создай улучшенную версию решения:
            1. Интегрируй все принятые предложения
            2. Сохрани авторский стиль
            3. Обеспечь логическую связность
            4. Выдели изменения маркерами [ДОБАВЛЕНО: ...] или [ИЗМЕНЕНО: ...]
            5. Убедись, что текст читается естественно
            
            Финальный текст должен быть цельным и гармоничным.
            """

        response = await self._make_llm_request(
            prompt, system_prompt, "text"
        )
        return response.get("text", "")

    # === Вспомогательные методы ===

    async def _make_llm_request(
            self,
            prompt: str,
            system_prompt: str = "",
            response_format: str = "text"
    ) -> Dict[str, Any]:
        """Выполнение запроса к LLM с fallback"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        last_error = None

        for provider in self.providers:
            try:
                response = await self._call_provider(
                    provider, prompt, system_prompt, response_format
                )
                if response:
                    return response
            except Exception as e:
                last_error = e
                print(f"Provider {provider.name} failed: {e}")
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

        if provider.name == "huggingface":
            return await self._call_huggingface(
                provider, prompt, system_prompt, response_format
            )
        # elif provider.name == "ollama":
        #     return await self._call_ollama(
        #         provider, prompt, system_prompt, response_format
        #     )
        # elif provider.name == "anthropic":
        #     return await self._call_anthropic(
        #         provider, prompt, system_prompt,response_format
        #     )
        # elif provider.name == "openai":
        #     return await self._call_openai(
        #         provider, prompt, system_prompt, response_format
        #     )
        else:
            raise ValueError(f"Unknown provider: {provider.name}")

    async def _call_huggingface(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str,
    ) -> Dict[str, Any]:
        """Вызов Hugging Face API"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        full_prompt = (
            f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt
            else f"User: {prompt}\nAssistant:"
        )

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": provider.max_tokens,
                "temperature": provider.temperature,
                "return_full_text": False,
                "do_sample": True
            }
        }

        async with self.session.post(
                provider.api_url, json=payload, headers=headers,
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
                    f"Hugging Face API error {response.status}: {error_text}")

    async def _call_ollama(
            self,
            provider: LLMProvider,
            prompt: str,
            system_prompt: str,
            response_format: str,
    ) -> Dict[str, Any]:
        """Вызов локального Ollama"""
        payload = {
            "model": provider.model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False,
            "options": {
                "temperature": provider.temperature,
                "num_predict": provider.max_tokens
            }
        }

        async with self.session.post(
                provider.api_url, json=payload, timeout=provider.timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data.get("response", "")
                return self._parse_response(content, response_format)
            else:
                error_text = await response.text()
                raise Exception(
                    f"Ollama API error {response.status}: {error_text}"
                )

    async def _call_anthropic(
            self, provider: LLMProvider, prompt: str, system_prompt: str,
            response_format: str
    ) -> Dict[str, Any]:
        """Вызов Anthropic Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": provider.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": provider.model,
            "max_tokens": provider.max_tokens,
            "temperature": provider.temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }

        async with self.session.post(
                provider.api_url,
                json=payload,
                headers=headers,
                timeout=provider.timeout
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data["content"][0]["text"]
                return self._parse_response(content, response_format)
            else:
                raise Exception(f"Anthropic API error: {response.status}")

    async def _call_openai(
            self, provider: LLMProvider, prompt: str, system_prompt: str,
            response_format: str
    ) -> Dict[str, Any]:
        """Вызов OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider.api_key}"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": provider.max_tokens,
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
                raise Exception(f"OpenAI API error: {response.status}")

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

    @staticmethod
    def _format_solutions_for_analysis(solutions: List[Solution]) -> str:
        """Форматирование решений для анализа"""
        if not solutions:
            return "Нет доступных решений для анализа."

        formatted = []
        for i, solution in enumerate(solutions[:30], 1):
            content = solution.current_content[:1000]
            if len(solution.current_content) > 1000:
                content += "... [обрезано]"

            formatted.append(f"""
                РЕШЕНИЕ #{i} (Автор: {solution.user_id[:8]}):
                {content}
                ---""")

        return "\n".join(formatted)

    @staticmethod
    def _format_solutions_for_detailed_analysis(
            solutions: List[Solution]
    ) -> str:
        """Детальное форматирование для комбинирования"""
        if not solutions:
            return "Нет доступных решений."

        formatted = []
        for i, solution in enumerate(solutions[:20], 1):
            content = solution.current_content[:1500]
            if len(solution.current_content) > 1500:
                content += "... [обрезано]"

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
    def generate_cache_key(operation: str,params: Dict[str, Any]) -> str:
        """Генерация ключа кэша для операции"""
        param_str = json.dumps(params, sort_keys=True)
        combined = f"{operation}:{param_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    @staticmethod
    async def check_huggingface_health(provider: LLMProvider) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {provider.api_key}"}


                async with session.head(
                        provider.api_url,
                        headers=headers,
                        timeout=5
                ) as response:
                    return {
                        "status": "healthy" if response.status in [
                            200, 401, 403
                        ] else "unhealthy",
                        "http_status": response.status
                    }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_ollama_health(provider: LLMProvider) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "http://localhost:11434/api/tags",
                        timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in
                                  data.get("models", [])]
                        model_available = provider.model in models

                        return {
                            "status": "healthy" if model_available else "degraded",
                            "models_available": models,
                            "target_model_available": model_available
                        }
                    else:
                        return {"status": "unhealthy",
                                "error": f"Ollama not responding: {response.status}"}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
