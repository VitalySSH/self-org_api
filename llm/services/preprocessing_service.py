import json
import re
from typing import Dict, Any, List, Tuple
from collections import Counter
import numpy as np

from datastorage.crud.datastorage import CRUDDataStorage
from datastorage.crud.interfaces.list import Filter, Operation
from datastorage.database.models import Solution, Challenge, SolutionPreprocessing


# try:
#     from .advanced_embedding_service import (
#         AdvancedEmbeddingService,
#         SENTENCE_TRANSFORMERS_AVAILABLE
#     )
# except ImportError:
#     SENTENCE_TRANSFORMERS_AVAILABLE = False
#     AdvancedEmbeddingService = None

SENTENCE_TRANSFORMERS_AVAILABLE = False
AdvancedEmbeddingService = None


class PreprocessingService:
    """
    Предобработка решений

    Поддерживает два режима embeddings:
    1. Легковесные (по умолчанию) - TF-IDF + n-grams + семантика
    2. Transformer (опционально) - sentence-transformers/all-MiniLM-L6-v2
    """

    def __init__(
            self,
            data_adapter,
            use_transformer_embeddings: bool = False
    ):
        """
        Args:
            data_adapter: Адаптер для работы с БД
            use_transformer_embeddings: Использовать ли transformer embeddings
        """
        self.data_adapter = data_adapter
        self.use_transformer_embeddings = use_transformer_embeddings

        # Инициализация embedding сервиса
        if use_transformer_embeddings:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_service = AdvancedEmbeddingService()
                print("✅ Используются transformer embeddings (all-MiniLM-L6-v2)")
            else:
                print("⚠️ sentence-transformers не установлен")
                print("   Установите: pip install sentence-transformers")
                print("   Используются легковесные embeddings")
                self.embedding_service = None
                self.use_transformer_embeddings = False
        else:
            self.embedding_service = None

        # Стоп-слова для русского языка
        self.stop_words = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как',
            'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к',
            'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь',
            'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни',
            'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам',
            'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они',
            'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их',
            'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже',
            'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому',
            'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти',
            'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем',
            'это', 'эти', 'при', 'два', 'об', 'другой', 'хоть', 'после', 'над',
            'больше', 'тот', 'через', 'эту', 'нас', 'про', 'всех', 'них', 'какая',
            'много', 'разве', 'три', 'эта', 'эти', 'свою', 'моя', 'впрочем', 'ту'
        }

    async def preprocess_solution(
            self,
            solution: Solution,
            challenge: Challenge
    ) -> Dict[str, Any]:
        """
        Предобработка решения

        Использует transformer или легковесные embeddings в зависимости от настроек
        """
        text = solution.current_content

        # 1. Генерация embedding (выбор метода)
        if self.use_transformer_embeddings and self.embedding_service:
            embedding = self.embedding_service.generate_embedding(text)
        else:
            embedding = self._generate_improved_embedding(text)

        # 2. Извлечение ключевых тезисов
        key_points = self._extract_key_points(text)

        # 3. Категоризация подхода
        category = self._classify_approach(text, challenge)

        # 4. Расчет метрик
        metrics = self._calculate_metrics(text)

        # 5. Сохраняем в БД
        ds = CRUDDataStorage(
            model=SolutionPreprocessing,
            session=self.data_adapter.session
        )

        preprocessing = await ds.first(
            filters=[
                Filter(field="solution_id", op=Operation.EQ, val=solution.id),
            ]
        )

        is_new = preprocessing is None
        if is_new:
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
            "metrics": metrics,
            "embedding_type": "transformer" if self.use_transformer_embeddings else "lightweight"
        }

    def _generate_improved_embedding(self, text: str, dim: int = 384) -> List[float]:
        """
        Легковесная генерация embedding (fallback)

        Использует комбинацию:
        1. TF-IDF взвешивание (60%)
        2. Character n-grams (25%)
        3. Позиционное кодирование (10%)
        4. Семантические кластеры (5%)
        """
        words = self._tokenize(text.lower())
        words = [w for w in words if w not in self.stop_words and len(w) > 2]

        if not words:
            return [0.0] * dim

        embedding = np.zeros(dim)

        # 1. TF-IDF компонента (60% весов)
        word_counts = Counter(words)
        total_words = len(words)

        for word, count in word_counts.items():
            tf = count / total_words
            idf = 1 + np.log(1 + len(word))
            weight = tf * idf

            for i in range(3):
                hash_val = (hash(word) + i * 12345) % dim
                embedding[hash_val] += weight * 0.6

        # 2. Character n-grams компонента (25% весов)
        ngrams = []
        for word in words:
            if len(word) >= 4:
                for n in [2, 3]:
                    for i in range(len(word) - n + 1):
                        ngrams.append(word[i:i + n])

        ngram_counts = Counter(ngrams)
        for ngram, count in ngram_counts.items():
            weight = count / len(ngrams) if ngrams else 0
            hash_val = hash(ngram) % dim
            embedding[hash_val] += weight * 0.25

        # 3. Позиционный компонент (10% весов)
        for idx, word in enumerate(words[:50]):
            position_weight = 1.0 / (1 + idx * 0.02)
            hash_val = hash(f"pos_{word}") % dim
            embedding[hash_val] += position_weight * 0.1

        # 4. Семантические кластеры (5% весов)
        semantic_clusters = self._get_semantic_clusters()
        for cluster_name, cluster_words in semantic_clusters.items():
            cluster_matches = sum(1 for w in words if w in cluster_words)
            if cluster_matches > 0:
                cluster_weight = cluster_matches / len(words)
                hash_val = hash(f"cluster_{cluster_name}") % dim
                embedding[hash_val] += cluster_weight * 0.05

        # Нормализация
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()

    @staticmethod
    def _get_semantic_clusters() -> Dict[str, set]:
        """Семантические кластеры для русского языка"""
        return {
            'technology': {
                'технология', 'система', 'алгоритм', 'программа', 'приложение',
                'платформа', 'сервис', 'api', 'данные', 'база', 'код', 'сервер',
                'интеграция', 'автоматизация', 'цифровой', 'онлайн', 'софт',
                'разработка', 'инструмент', 'решение', 'интерфейс'
            },
            'social': {
                'люди', 'общество', 'сообщество', 'команда', 'группа', 'участник',
                'взаимодействие', 'коммуникация', 'организация', 'культура',
                'мотивация', 'сотрудничество', 'партнерство', 'отношение', 'связь',
                'социальный', 'человек', 'коллектив', 'координация'
            },
            'business': {
                'бизнес', 'компания', 'рынок', 'продажа', 'клиент', 'доход',
                'прибыль', 'стоимость', 'цена', 'инвестиция', 'финансы', 'модель',
                'стратегия', 'конкуренция', 'маркетинг', 'продукт', 'услуга',
                'монетизация', 'экономика'
            },
            'process': {
                'процесс', 'метод', 'подход', 'способ', 'этап', 'шаг', 'алгоритм',
                'последовательность', 'порядок', 'структура', 'организация',
                'планирование', 'выполнение', 'реализация', 'внедрение', 'цикл'
            },
            'analysis': {
                'анализ', 'исследование', 'изучение', 'данные', 'метрика',
                'измерение', 'оценка', 'тестирование', 'эксперимент', 'результат',
                'показатель', 'статистика', 'модель', 'проверка', 'изучение'
            },
            'creative': {
                'идея', 'креатив', 'творчество', 'инновация', 'новый', 'оригинальный',
                'уникальный', 'необычный', 'эксперимент', 'концепция', 'видение',
                'воображение', 'вдохновение', 'изобретение'
            },
            'education': {
                'обучение', 'образование', 'учеба', 'знание', 'навык', 'компетенция',
                'курс', 'тренинг', 'практика', 'опыт', 'развитие', 'изучение',
                'преподавание', 'методика', 'материал'
            }
        }

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Токенизация с нормализацией"""
        text = re.sub(r'[^\w\s]', ' ', text)
        return [w.strip() for w in text.split() if w.strip()]

    def _extract_key_points(self, text: str, max_sentences: int = 3) -> str:
        """Извлечение ключевых тезисов"""
        sentences = self._split_sentences(text)

        if len(sentences) <= max_sentences:
            return '. '.join(sentences)

        all_words = self._tokenize(text.lower())
        keywords = [w for w in all_words if w not in self.stop_words and len(w) > 3]
        keyword_counts = Counter(keywords)
        top_keywords = set([w for w, _ in keyword_counts.most_common(20)])

        sentence_scores = []
        for i, sent in enumerate(sentences):
            sent_words = set(self._tokenize(sent.lower()))
            score = len(sent_words & top_keywords)

            if i == 0:
                score *= 1.5
            if i == len(sentences) - 1:
                score *= 1.2

            sentence_scores.append((i, score, sent))

        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected = sentence_scores[:max_sentences]

        selected.sort(key=lambda x: x[0])
        return '. '.join([s[2] for s in selected])

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Разбивка на предложения"""
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    @staticmethod
    def _classify_approach(text: str, challenge: Challenge) -> str:
        """Классификация подхода"""
        text_lower = text.lower()

        categories = {
            'technical': [
                'технология', 'система', 'алгоритм', 'программа', 'данные',
                'автоматизация', 'платформа', 'приложение', 'код', 'api',
                'база', 'сервер', 'интеграция', 'разработка', 'софт'
            ],
            'social': [
                'люди', 'общество', 'сообщество', 'команда', 'группа',
                'взаимодействие', 'коммуникация', 'организация', 'культура',
                'мотивация', 'партнерство', 'сотрудничество', 'отношения'
            ],
            'creative': [
                'идея', 'креатив', 'инновация', 'нестандартный',
                'оригинальный', 'творческий', 'необычный', 'новый',
                'экспериментальный', 'революционный', 'уникальный'
            ],
            'analytical': [
                'анализ', 'исследование', 'изучение', 'данные', 'статистика',
                'метрика', 'измерение', 'оценка', 'эксперимент', 'тестирование',
                'модель', 'проверка'
            ],
            'practical': [
                'практика', 'опыт', 'применение', 'реализация', 'внедрение',
                'использование', 'пример', 'случай', 'результат', 'эффект',
                'выгода', 'действие'
            ]
        }

        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score

        if max(scores.values()) == 0:
            return 'general'

        return max(scores.items(), key=lambda x: x[1])[0]

    def _calculate_metrics(self, text: str) -> Dict[str, Any]:
        """Расчет метрик качества"""
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
        """Оценка структурированности (0-1)"""
        score = 0.0

        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.3

        if re.search(r'[\n-•]\s*', text):
            score += 0.3

        sentences = self._split_sentences(text)
        if sentences:
            avg_len = sum(len(s) for s in sentences) / len(sentences)
            if 50 < avg_len < 200:
                score += 0.2

        if re.search(r'\n[А-ЯЁ][А-ЯЁ\s]+\n', text):
            score += 0.2

        return min(score, 1.0)

    def _calculate_keyword_density(self, text: str) -> float:
        """Плотность ключевых слов"""
        words = self._tokenize(text.lower())
        if not words:
            return 0.0

        keywords = [w for w in words if w not in self.stop_words and len(w) > 4]
        return len(keywords) / len(words)

    async def find_similar_solutions(
            self,
            solution_id: str,
            top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Поиск похожих решений через cosine similarity

        Работает с обоими типами embeddings
        """
        ds = CRUDDataStorage(
            model=SolutionPreprocessing,
            session=self.data_adapter.session
        )

        target_prep = await ds.first(
            filters=[
                Filter(field="solution_id", op=Operation.EQ, val=solution_id)
            ]
        )

        if not target_prep:
            return []

        target_embedding = np.array(json.loads(target_prep.embedding))

        solution = await self.data_adapter.get_solution(solution_id)
        other_solutions = await self.data_adapter.get_other_solutions_for_challenge(
            solution.challenge_id, solution.user_id
        )

        similarities = []
        for other in other_solutions:
            other_prep = await ds.first(
                filters=[
                    Filter(field="solution_id", op=Operation.EQ, val=other.id)
                ]
            )
            if other_prep:
                other_embedding = np.array(json.loads(other_prep.embedding))
                similarity = self._cosine_similarity(target_embedding, other_embedding)
                similarities.append((other.id, float(similarity)))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def find_diverse_solutions(
            self,
            all_solutions: List,
            target_count: int = 15
    ) -> List:
        """
        Дивергентный отбор: находит максимально различающиеся решения

        Использует MMR (Maximal Marginal Relevance)
        Работает с обоими типами embeddings
        """
        if len(all_solutions) <= target_count:
            return all_solutions

        ds = CRUDDataStorage(
            model=SolutionPreprocessing,
            session=self.data_adapter.session
        )

        # Получаем embeddings всех решений
        embeddings_map = {}
        for sol in all_solutions:
            prep = await ds.first(
                filters=[
                    Filter(field="solution_id", op=Operation.EQ, val=sol.id)
                ]
            )
            if prep:
                embeddings_map[sol.id] = np.array(json.loads(prep.embedding))

        if len(embeddings_map) < target_count:
            return all_solutions

        # Применяем дивергентную стратегию
        selected = await self._maximal_marginal_relevance(
            embeddings_map,
            target_count,
            lambda_param=0.7
        )

        return [sol for sol in all_solutions if sol.id in selected]

    async def _maximal_marginal_relevance(
            self,
            embeddings_map: Dict[str, np.ndarray],
            target_count: int,
            lambda_param: float = 0.7
    ) -> List[str]:
        """
        MMR алгоритм для выбора разнообразных решений

        Args:
            embeddings_map: Словарь {solution_id: embedding}
            target_count: Количество решений для отбора
            lambda_param: Вес diversity vs relevance (0.7 = больше diversity)

        Returns:
            List[solution_id] отобранных решений
        """
        solution_ids = list(embeddings_map.keys())
        embeddings = np.array([embeddings_map[sid] for sid in solution_ids])

        # Начинаем с самого "среднего" решения (центроид)
        centroid = np.mean(embeddings, axis=0)
        similarities_to_centroid = [
            self._cosine_similarity(emb, centroid)
            for emb in embeddings
        ]

        selected_indices = [np.argmax(similarities_to_centroid)]
        selected_ids = [solution_ids[selected_indices[0]]]
        remaining_indices = set(range(len(solution_ids))) - set(selected_indices)

        # Итеративно добавляем наиболее различающиеся решения
        while len(selected_indices) < target_count and remaining_indices:
            mmr_scores = []

            for idx in remaining_indices:
                # Relevance: схожесть с центроидом
                relevance = similarities_to_centroid[idx]

                # Diversity: максимальная схожесть с уже выбранными
                max_similarity = max(
                    self._cosine_similarity(
                        embeddings[idx],
                        embeddings[selected_idx]
                    )
                    for selected_idx in selected_indices
                )

                # MMR score: баланс между relevance и diversity
                mmr_score = lambda_param * relevance - (
                            1 - lambda_param
                ) * max_similarity
                mmr_scores.append((idx, mmr_score))

            # Выбираем решение с максимальным MMR score
            best_idx, _ = max(mmr_scores, key=lambda x: x[1])
            selected_indices.append(best_idx)
            selected_ids.append(solution_ids[best_idx])
            remaining_indices.remove(best_idx)

        return selected_ids

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity между векторами"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))
