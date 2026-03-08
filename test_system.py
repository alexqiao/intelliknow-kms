#!/usr/bin/env python3
"""测试脚本 - 验证 IntelliKnow KMS 核心功能"""

import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试核心模块导入"""
    print("🧪 测试模块导入...")
    try:
        from app.database import init_db, SessionLocal, Intent
        from app.services.vector_store import VectorStore
        print("  ✅ 数据库模块")
        print("  ✅ 向量存储模块")
        return True
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False

def test_database():
    """测试数据库初始化"""
    print("\n🧪 测试数据库初始化...")
    try:
        from app.database import init_db, SessionLocal, Intent
        init_db()

        session = SessionLocal()
        intents = session.query(Intent).all()
        print(f"  ✅ 数据库初始化成功")
        print(f"  ✅ 默认意图数量: {len(intents)}")
        for intent in intents:
            print(f"     - {intent.name}: {intent.description}")
        session.close()
        return True
    except Exception as e:
        print(f"  ❌ 数据库测试失败: {e}")
        return False

def test_vector_store():
    """测试向量存储"""
    print("\n🧪 测试向量存储...")
    try:
        from app.services.vector_store import VectorStore
        import numpy as np

        vs = VectorStore(dimension=1024)

        # 测试添加向量
        test_vectors = np.random.rand(3, 1024).tolist()
        test_chunks = ["测试文本1", "测试文本2", "测试文本3"]
        ids = vs.add_vectors(test_vectors, test_chunks, doc_id=1)

        print(f"  ✅ 向量存储初始化成功")
        print(f"  ✅ 添加了 {len(ids)} 个向量")

        # 测试搜索
        query_vector = np.random.rand(1024).tolist()
        results = vs.search(query_vector, top_k=2)
        print(f"  ✅ 搜索返回 {len(results)} 个结果")

        return True
    except Exception as e:
        print(f"  ❌ 向量存储测试失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🧠 IntelliKnow KMS - 系统测试")
    print("=" * 50)

    results = []
    results.append(("模块导入", test_imports()))
    results.append(("数据库", test_database()))
    results.append(("向量存储", test_vector_store()))

    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
