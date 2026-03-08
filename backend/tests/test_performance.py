#!/usr/bin/env python3
"""性能测试"""
import sys
import os
import time
import asyncio
from unittest.mock import patch, AsyncMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def mock_chat_completion(messages):
    """Mock chat completion with different responses based on input"""
    content = str(messages)
    if "Classify" in content or "classify" in content:
        return '{"intent": "HR", "confidence": 0.95}'
    return "This is a mocked RAG response."

async def test_performance():
    from app.services.llm_service import QwenLLMService
    from app.dependencies import vector_store_instance
    from app.services.orchestrator import QueryOrchestrator
    from app.database import SessionLocal
    from app.config import get_settings

    print("🧪 性能测试\n")
    settings = get_settings()

    with patch.object(QwenLLMService, 'generate_embeddings', new_callable=AsyncMock) as mock_embeddings, \
         patch.object(QwenLLMService, 'chat_completion', new_callable=AsyncMock) as mock_chat:

        # Configure mocks
        mock_embeddings.return_value = [[0.1] * 1024]
        mock_chat.side_effect = mock_chat_completion

        llm = QwenLLMService(settings.qwen_api_key)

        # 测试并发查询
        print("1️⃣ 测试并发查询（5个）...")
        queries = [
            "What is the vacation policy?",
            "How many days off?",
            "Legal terms?",
            "Finance policy?",
            "HR contact?"
        ]

        start = time.time()
        tasks = []
        db_sessions = []

        try:
            for q in queries:
                db = SessionLocal()
                db_sessions.append(db)
                orchestrator = QueryOrchestrator(llm, vector_store_instance, db)
                tasks.append(orchestrator.process_query(q, "test", "user1"))

            results = await asyncio.gather(*tasks)
            elapsed = (time.time() - start) * 1000

            print(f"   ✓ 完成 {len(results)} 个查询")
            print(f"   总时间: {elapsed:.0f}ms")
            print(f"   平均: {elapsed/len(results):.0f}ms/查询")
        finally:
            for db in db_sessions:
                db.close()

    print("\n✅ 性能测试完成")

if __name__ == "__main__":
    asyncio.run(test_performance())
