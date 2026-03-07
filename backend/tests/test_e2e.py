#!/usr/bin/env python3
"""端到端测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_e2e():
    from app.services.llm_service import QwenLLMService
    from app.services.vector_store import VectorStore
    from app.services.orchestrator import QueryOrchestrator
    from app.database import SessionLocal
    from app.config import get_settings

    print("🧪 端到端测试\n")
    settings = get_settings()
    llm = QwenLLMService(settings.qwen_api_key)
    vector_store = VectorStore(dimension=1024)
    db = SessionLocal()
    orchestrator = QueryOrchestrator(llm, vector_store, db)

    # 测试1: 空查询
    print("1️⃣ 测试空查询...")
    try:
        result = await orchestrator.process_query("", "test", "user1")
        print(f"   ✓ 处理成功: {result['response'][:50]}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    # 测试2: 超长查询
    print("\n2️⃣ 测试超长查询...")
    long_query = "What is the policy? " * 100
    try:
        result = await orchestrator.process_query(long_query, "test", "user1")
        print(f"   ✓ 处理成功，响应时间: {result['response_time_ms']}ms")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    # 测试3: 无匹配结果
    print("\n3️⃣ 测试无匹配查询...")
    try:
        result = await orchestrator.process_query("xyz123abc", "test", "user1")
        print(f"   ✓ 响应: {result['response'][:50]}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    db.close()
    print("\n✅ 测试完成")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_e2e())
