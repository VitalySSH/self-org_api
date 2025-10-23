import re


class TextOptimizer:
    """Оптимизатор текста решений для промптов."""

    def clean_and_optimize(self, text: str, preserve_structure: bool = True) -> str:
        if not text or not isinstance(text, str):
            return ""

        # Этап 1: Удаление MD-разметки
        text = self._remove_markdown(text)

        # Этап 2: Нормализация пробелов и переносов
        text = self._normalize_whitespace(text)

        # Этап 3: Оптимизация структуры (опционально)
        if preserve_structure:
            text = self._optimize_structure(text)

        return text.strip()

    @staticmethod
    def _remove_markdown(text: str) -> str:
        """
        Удаление Markdown-разметки с сохранением содержания.

        Удаляет:
        - Заголовки (#, ##, ###)
        - Жирный/курсив (**, *, _, __)
        - Ссылки [text](url)
        - Код (`, ```, ~~~)
        - Списки (-, *, +, 1.)
        - Цитаты (>)
        - Горизонтальные линии (---, ___, ***)
        - Таблицы (|)

        Сохраняет содержимое полностью!
        """
        # Заголовки: ### Заголовок → Заголовок
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Жирный текст: **text** или __text__ → text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)

        # Курсив: *text* или _text_ → text
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)

        # Зачёркнутый: ~~text~~ → text
        text = re.sub(r'~~(.+?)~~', r'\1', text)

        # Ссылки: [text](url) → text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Изображения: ![alt](url) → alt
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)

        # Инлайн код: `code` → code
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Блоки кода: ```code``` или ~~~code~~~ → code
        text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).strip('`'), text)
        text = re.sub(r'~~~[\s\S]*?~~~', lambda m: m.group(0).strip('~'), text)

        # Списки: сохраняем содержимое, удаляем маркеры
        # - item → item
        # * item → item
        # + item → item
        # 1. item → item
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Цитаты: > text → text
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

        # Горизонтальные линии: ---, ***, ___ → удаляем полностью
        text = re.sub(r'^[\s]*[-*_]{3,}[\s]*$', '', text, flags=re.MULTILINE)

        # Таблицы: упрощаем до текста
        # | col1 | col2 | → col1, col2
        text = re.sub(r'\|', ',', text)
        text = re.sub(r'^[\s]*[-:]+[\s]*$', '', text, flags=re.MULTILINE)

        # HTML теги: <tag>text</tag> → text
        text = re.sub(r'<[^>]+>', '', text)

        return text

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """
        Нормализация пробелов и переносов строк.

        - Удаляет лишние пробелы
        - Сокращает множественные переносы до максимум 2
        - Убирает пробелы в начале/конце строк
        """
        # Удаляем пробелы в начале и конце каждой строки
        text = re.sub(r'^[ \t]+|[ \t]+$', '', text, flags=re.MULTILINE)

        # Заменяем множественные пробелы на один
        text = re.sub(r'[ \t]+', ' ', text)

        # Заменяем 3+ переноса строки на 2 (параграфы)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Удаляем пробелы перед знаками препинания
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)

        return text

    @staticmethod
    def _optimize_structure(text: str) -> str:
        """
        Оптимизация структуры текста для компактности.

        - Объединяет короткие абзацы в логические блоки
        - Сохраняет структуру длинных рассуждений
        """
        paragraphs = text.split('\n\n')
        optimized = []
        buffer = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Если параграф короткий (< 100 символов), накапливаем
            if len(para) < 100 and len(buffer) < 3:
                buffer.append(para)
            else:
                # Сбрасываем буфер
                if buffer:
                    optimized.append(' '.join(buffer))
                    buffer = []
                optimized.append(para)

        # Добавляем остаток буфера
        if buffer:
            optimized.append(' '.join(buffer))

        return '\n\n'.join(optimized)
