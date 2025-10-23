from typing import List
from llm.models.lab import LLMProvider


def create_default_llm_providers() -> List[LLMProvider]:
    return [
        LLMProvider(
            name="together",
            api_url="https://api.together.xyz/v1/chat/completions",
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            max_tokens=3000,
            max_context_tokens=8192,
            safe_usage_ratio=0.75,
            temperature=0.7,
            timeout=120,
            priority=1
        ),
        LLMProvider(
            name="together",
            api_url="https://api.together.xyz/v1/chat/completions",
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            max_tokens=3000,
            max_context_tokens=8192,
            safe_usage_ratio=0.8,
            temperature=0.7,
            timeout=90,
            priority=2
        ),
        # LLMProvider(
        #     name="groq",
        #     api_url="https://api.groq.com/openai/v1/chat/completions",
        #     model="llama-3.3-70b-versatile",
        #     max_tokens=6000,
        #     max_context_tokens=8192,
        #     safe_usage_ratio=0.7,
        #     temperature=0.7,
        #     timeout=30,
        #     priority=3
        # ),
        # LLMProvider(
        #     name="huggingface",
        #     api_url="https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct",
        #     model="Qwen/Qwen2.5-7B-Instruct",
        #     max_tokens=2000,
        #     max_context_tokens=32768,
        #     safe_usage_ratio=0.6,
        #     temperature=0.7,
        #     timeout=45,
        #     priority=4
        # ),
    ]


def create_provider_for_task(task_type: str, solutions_count: int) -> str:
    """
    Выбирает оптимальный провайдер на основе типа задачи и количества решений

    Args:
        task_type: "directions", "ideas", "improvements", "criticism"
        solutions_count: количество решений для анализа

    Returns:
        Имя провайдера
    """
    if solutions_count <= 12 and task_type in ["improvements", "criticism"]:
        return "together"

    if task_type in ["ideas", "directions"] or solutions_count > 12:
        return "together"

    return "together"