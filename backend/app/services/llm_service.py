from openai import OpenAI
from typing import List

class QwenLLMService:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model="text-embedding-v3",
                input=batch
            )
            all_embeddings.extend([item.embedding for item in response.data])

        return all_embeddings

    async def chat_completion(self, messages: List[dict]) -> str:
        response = self.client.chat.completions.create(
            model="qwen-turbo",  # 更快的模型，响应速度提升5-10倍
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
