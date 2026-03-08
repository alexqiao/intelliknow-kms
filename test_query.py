#!/usr/bin/env python3
"""测试查询编排功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_query():
    from app.services.llm_service import QwenLLMService
    from app.dependencies import vector_store_instance
    from app.services.orchestrator import QueryOrchestrator
    from app.database import SessionLocal
    from app.config import get_settings

    print("🧪 测试查询编排流程\n")

    settings = get_settings()
    llm = QwenLLMService(settings.qwen_api_key)
    db = SessionLocal()

    orchestrator = QueryOrchestrator(llm, vector_store_instance, db)

    # 测试查询
    test_queries = [
        "What is the vacation policy?",
        "How many days of annual leave do I get?",
        "What are the legal terms?"
    ]

    for query in test_queries:
        print(f"\n📝 查询: {query}")
        result = await orchestrator.process_query(query, "test", "test_user")

        print(f"  意图: {result['intent']} (置信度: {result['confidence']:.2f})")
        print(f"  响应时间: {result['response_time_ms']}ms")
        print(f"  回答: {result['response'][:100]}...")

    db.close()
    print("\n✅ 查询测试完成！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query())
