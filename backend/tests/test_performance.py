#!/usr/bin/env python3
"""性能测试"""
import sys
import os
import time
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_performance():
    from app.services.llm_service import QwenLLMService
    from app.services.vector_store import VectorStore
    from app.services.orchestrator import QueryOrchestrator
    from app.database import SessionLocal
    from app.config import get_settings

    print("🧪 性能测试\n")
    settings = get_settings()
    llm = QwenLLMService(settings.qwen_api_key)
    vector_store = VectorStore(dimension=1024)

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
    for q in queries:
        db = SessionLocal()
        orchestrator = QueryOrchestrator(llm, vector_store, db)
        tasks.append(orchestrator.process_query(q, "test", "user1"))

    results = await asyncio.gather(*tasks)
    elapsed = (time.time() - start) * 1000

    print(f"   ✓ 完成 {len(results)} 个查询")
    print(f"   总时间: {elapsed:.0f}ms")
    print(f"   平均: {elapsed/len(results):.0f}ms/查询")

    for db in [SessionLocal()]:
        db.close()

    print("\n✅ 性能测试完成")

if __name__ == "__main__":
    asyncio.run(test_performance())
