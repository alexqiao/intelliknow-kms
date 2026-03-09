#!/usr/bin/env python3
"""测试意图过滤"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_intent_filtering():
    from app.dependencies import vector_store_instance, llm_service_instance
    from app.services.orchestrator import QueryOrchestrator
    from app.database import SessionLocal

    print("🧪 测试意图过滤功能\n")
    db = SessionLocal()
    orchestrator = QueryOrchestrator(llm_service_instance, vector_store_instance, db)

    # 测试 HR 查询
    print("1️⃣ 测试 HR 查询...")
    result = await orchestrator.process_query("How many vacation days?", "test", "user1")
    print(f"   意图: {result['intent']}")
    print(f"   置信度: {result['confidence']}")
    print(f"   响应: {result['response'][:80]}...")

    db.close()
    print("\n✅ 意图过滤测试完成")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intent_filtering())
