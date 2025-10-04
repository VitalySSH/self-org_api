from typing import List

from llm.services.llm_service import LLMProvider


def create_default_llm_providers() -> List[LLMProvider]:
    """Создание конфигурации провайдеров по умолчанию"""
    return [
        LLMProvider(
            name="huggingface",
            api_url="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            model="mistralai/Mistral-7B-Instruct-v0.1",
            # api_url="https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            # model="microsoft/DialoGPT-medium",
            max_tokens=4000,
            temperature=0.7,
            priority=1
        ),
        # LLMProvider(
        #     name="ollama",
        #     api_url="http://localhost:11434/api/generate",
        #     model="llama2:7b",
        #     max_tokens=4000,
        #     temperature=0.7,
        #     priority=2
        # ),
        # LLMProvider(
        #     name="anthropic",
        #     api_url="https://api.anthropic.com/v1/messages",
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=4000,
        #     temperature=0.7,
        #     priority=3
        # ),
        # LLMProvider(
        #     name="openai",
        #     api_url="https://api.openai.com/v1/chat/completions",
        #     model="gpt-4o-mini",
        #     max_tokens=4000,
        #     temperature=0.7,
        #     priority=4
        # )
    ]
