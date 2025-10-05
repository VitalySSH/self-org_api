import json
import re
from typing import Dict, Any, List
from collections import Counter
import numpy as np

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.list import Filter, Operation
from datastorage.database.models import Solution, Challenge, \
    SolutionPreprocessing


class PreprocessingService:
    """Предобработка решений без использования LLM"""

    def __init__(self, data_adapter):
        self.data_adapter = data_adapter

        # Стоп-слова для русского языка (базовый набор)
        self.stop_words = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как',
            'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к',
            'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь',
            'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни',
            'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам',
            'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они',
            'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их',
            'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз',
            'тоже',
            'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того',
            'потому',
            'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один',
            'почти',
            'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем'
        }

    async def preprocess_solution(
            self,
            solution: Solution,
            challenge: Challenge
    ) -> Dict[str, Any]:
        """
        Предобработка решения при создании/изменении

        Args:
            solution: Решение участника
            challenge: Задача, к которой относится решение

        Returns:
            Dict с предобработанными данными
        """

        text = solution.current_content

        # 1. Генерация простого embedding (без LLM)
        embedding = self._generate_simple_embedding(text)

        # 2. Извлечение ключевых тезисов
        key_points = self._extract_key_points(text)

        # 3. Категоризация подхода
        category = self._classify_approach(text, challenge)

        # 4. Расчет метрик
        metrics = self._calculate_metrics(text)

        # 5. Сохраняем в БД
        ds = CRUDDataStorage(model=SolutionPreprocessing,
                             session=self.data_adapter.session)
        is_new = False
        preprocessing = await ds.first(
            filters=[
                Filter(field="solution_id", op=Operation.EQ, val=solution.id),
            ]
        )
        if preprocessing is None:
            is_new = True
            preprocessing = SolutionPreprocessing()
        preprocessing.solution = solution
        preprocessing.embedding = json.dumps(embedding)
        preprocessing.key_points = key_points
        preprocessing.category = category
        preprocessing.metrics = json.dumps(metrics)

        if is_new:
            await ds.create(instance=preprocessing)

        await self.data_adapter.session.commit()

        return {
            "embedding": embedding,
            "key_points": key_points,
            "category": category,
            "metrics": metrics
        }

    def _generate_simple_embedding(self, text: str, dim: int = 384) -> List[
        float]:
        """
        Генерация простого embedding без внешних моделей

        Использует TF-IDF подобный подход + хеширование
        Этого достаточно для базового semantic search

        В будущем можно заменить на sentence-transformers
        """
        # Токенизация
        words = self._tokenize(text.lower())

        # Удаляем стоп-слова
        words = [w for w in words if w not in self.stop_words and len(w) > 2]

        # Частоты слов
        word_counts = Counter(words)
        total_words = len(words)

        # Создаем embedding через хеширование слов
        embedding = np.zeros(dim)

        for word, count in word_counts.items():
            # Хешируем слово в индекс
            hash_val = hash(word) % dim
            # TF-IDF like вес
            tf = count / total_words
            embedding[hash_val] += tf

        # Нормализация
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()

    def _tokenize(self, text: str) -> List[str]:
        """Простая токенизация по словам"""
        # Удаляем пунктуацию и разбиваем по пробелам
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()

    def _extract_key_points(self, text: str, max_sentences: int = 3) -> str:
        """
        Извлечение ключевых тезисов (2-3 предложения)

        Использует эвристику:
        - Первое предложение (обычно содержит главную мысль)
        - Предложения с наибольшим количеством ключевых слов
        """
        # Разбиваем на предложения
        sentences = self._split_sentences(text)

        if len(sentences) <= max_sentences:
            return '. '.join(sentences)

        # Извлекаем ключевые слова из всего текста
        all_words = self._tokenize(text.lower())
        keywords = [w for w in all_words if
                    w not in self.stop_words and len(w) > 3]
        keyword_counts = Counter(keywords)
        top_keywords = set([w for w, _ in keyword_counts.most_common(20)])

        # Оцениваем важность каждого предложения
        sentence_scores = []
        for i, sent in enumerate(sentences):
            sent_words = set(self._tokenize(sent.lower()))
            # Количество топ-ключевых слов в предложении
            score = len(sent_words & top_keywords)
            # Бонус для первого предложения
            if i == 0:
                score *= 1.5
            sentence_scores.append((i, score, sent))

        # Сортируем по важности и берем топ N
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected = sentence_scores[:max_sentences]

        # Возвращаем в исходном порядке
        selected.sort(key=lambda x: x[0])
        return '. '.join([s[2] for s in selected])

    def _split_sentences(self, text: str) -> List[str]:
        """Разбивка текста на предложения"""
        # Простая эвристика: точка + пробел/конец строки
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _classify_approach(self, text: str, challenge: Challenge) -> str:
        """
        Классификация подхода решения

        Категории:
        - technical: технический/инженерный подход
        - social: социальный/организационный
        - creative: креативный/нестандартный
        - analytical: аналитический/исследовательский
        - practical: практический/прикладной
        """
        text_lower = text.lower()

        # Ключевые слова для каждой категории
        categories = {
            'technical': ['технология', 'система', 'алгоритм', 'программа',
                          'данные', 'автоматизация', 'платформа', 'приложение',
                          'код', 'api', 'база', 'сервер', 'интеграция'],
            'social': ['люди', 'общество', 'сообщество', 'команда', 'группа',
                       'взаимодействие', 'коммуникация', 'организация',
                       'культура',
                       'мотивация', 'партнерство', 'сотрудничество'],
            'creative': ['идея', 'креатив', 'инновация', 'нестандартный',
                         'оригинальный', 'творческий', 'необычный',
                         'новый подход',
                         'экспериментальный', 'революционный'],
            'analytical': ['анализ', 'исследование', 'изучение', 'данные',
                           'статистика', 'метрика', 'измерение', 'оценка',
                           'эксперимент', 'тестирование', 'модель'],
            'practical': ['практика', 'опыт', 'применение', 'реализация',
                          'внедрение', 'использование', 'пример', 'случай',
                          'результат', 'эффект', 'выгода']
        }

        # Подсчитываем совпадения
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score

        # Возвращаем категорию с максимальным скором
        if max(scores.values()) == 0:
            return 'general'

        return max(scores.items(), key=lambda x: x[1])[0]

    def _calculate_metrics(self, text: str) -> Dict[str, Any]:
        """
        Расчет метрик качества решения

        Метрики:
        - length: длина текста
        - structure_score: оценка структурированности
        - keyword_density: плотность ключевых слов
        - readability: оценка читаемости
        """
        words = self._tokenize(text)
        sentences = self._split_sentences(text)

        return {
            "length": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "structure_score": self._assess_structure(text),
            "keyword_density": self._calculate_keyword_density(text),
            "has_lists": bool(re.search(r'[\n-•]\s*', text)),
            "has_numbers": bool(re.search(r'\d', text))
        }

    def _assess_structure(self, text: str) -> float:
        """
        Оценка структурированности текста (0-1)

        Учитывает:
        - Наличие абзацев
        - Наличие списков
        - Разумную длину абзацев
        """
        score = 0.0

        # Наличие абзацев
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.3

        # Наличие списков или перечислений
        if re.search(r'[\n-•]\s*', text):
            score += 0.3

        # Разумная длина предложений
        sentences = self._split_sentences(text)
        if sentences:
            avg_len = sum(len(s) for s in sentences) / len(sentences)
            if 50 < avg_len < 200:
                score += 0.2

        # Наличие заголовков или выделений
        if re.search(r'\n[А-ЯЁ][А-ЯЁ\s]+\n', text):
            score += 0.2

        return min(score, 1.0)

    def _calculate_keyword_density(self, text: str) -> float:
        """
        Расчет плотности ключевых слов

        Ключевые слова = слова длиннее 4 символов, не стоп-слова
        """
        words = self._tokenize(text.lower())
        if not words:
            return 0.0

        keywords = [w for w in words if
                    w not in self.stop_words and len(w) > 4]
        return len(keywords) / len(words)

    async def find_similar_solutions(
            self,
            solution_id: str,
            top_k: int = 10
    ) -> List[tuple]:
        """
        Поиск похожих решений через cosine similarity embeddings

        Returns:
            List[(solution_id, similarity_score)]
        """
        # Получаем embedding целевого решения
        ds = CRUDDataStorage(model=SolutionPreprocessing,
                             session=self.data_adapter.session)
        target_prep = await ds.first(
            filters=[
                Filter(field="solution_id", op=Operation.EQ, val=solution_id)
            ]
        )

        if not target_prep:
            return []

        target_embedding = np.array(json.loads(target_prep.embedding))

        # Получаем все другие предобработки из той же задачи
        solution = await self.data_adapter.get_solution(solution_id)
        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        # Считаем similarity
        similarities = []
        for other in other_solutions:
            other_prep = await ds.first(
                filters=[
                    Filter(field="solution_id", op=Operation.EQ, val=other.id)]
            )
            if other_prep:
                other_embedding = np.array(json.loads(other_prep.embedding))
                # Cosine similarity
                similarity = np.dot(target_embedding, other_embedding)
                similarities.append((other.id, float(similarity)))

        # Сортируем по убыванию similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
