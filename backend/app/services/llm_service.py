from openai import AsyncOpenAI
from typing import List

class QwenLLMService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model="text-embedding-v3",
                input=batch
            )
            all_embeddings.extend([item.embedding for item in response.data])

        return all_embeddings

    async def chat_completion(self, messages: List[dict]) -> str:
        response = await self.client.chat.completions.create(
            model="qwen-turbo",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content


class GeminiLLMService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model="gemini-embedding-001",
                input=batch,
                dimensions=3072
            )
            all_embeddings.extend([item.embedding for item in response.data])

        return all_embeddings

    async def chat_completion(self, messages: List[dict]) -> str:
        response = await self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content


def get_llm_service(provider: str, settings):
    """Factory function to get the appropriate LLM service based on provider"""
    if provider == "gemini":
        return GeminiLLMService(settings.gemini_api_key)
    else:
        return QwenLLMService(settings.qwen_api_key)
