#!/usr/bin/env python3
"""端到端测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e():
    print("🧪 端到端测试\n")

    # 测试1: 空查询
    print("1️⃣ 测试空查询...")
    try:
        response = client.post("/api/query", json={
            "query": "",
            "source": "test",
            "user_id": "user1"
        })
        result = response.json()
        print(f"   ✓ 处理成功: {result['response'][:50]}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    # 测试2: 超长查询
    print("\n2️⃣ 测试超长查询...")
    long_query = "What is the policy? " * 100
    try:
        response = client.post("/api/query", json={
            "query": long_query,
            "source": "test",
            "user_id": "user1"
        })
        result = response.json()
        print(f"   ✓ 处理成功，响应时间: {result['response_time_ms']}ms")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    # 测试3: 无匹配结果
    print("\n3️⃣ 测试无匹配查询...")
    try:
        response = client.post("/api/query", json={
            "query": "xyz123abc",
            "source": "test",
            "user_id": "user1"
        })
        result = response.json()
        print(f"   ✓ 响应: {result['response'][:50]}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_e2e()
