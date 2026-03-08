#!/usr/bin/env python3
"""测试文档上传功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_upload():
    from app.services.llm_service import QwenLLMService
    from app.dependencies import vector_store_instance
    from app.services.document_processor import DocumentProcessor
    from app.database import SessionLocal, init_db
    from app.config import get_settings

    print("🧪 测试文档上传流程\n")

    # 初始化
    settings = get_settings()
    print(f"✓ 配置加载成功")
    print(f"  API Key: {settings.qwen_api_key[:10]}..." if settings.qwen_api_key else "  ⚠️  未配置 API Key")

    # 测试 LLM 服务
    print("\n📡 测试 Qwen API 连接...")
    try:
        llm = QwenLLMService(settings.qwen_api_key)
        embeddings = await llm.generate_embeddings(["测试文本"])
        print(f"✓ API 连接成功，向量维度: {len(embeddings[0])}")
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        return

    # 测试文档处理
    print("\n📄 测试文档处理...")
    test_file = "sample_docs/AKP.docx"
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        return

    try:
        db = SessionLocal()
        processor = DocumentProcessor(llm, vector_store_instance, db)

        # 模拟文档记录
        from app.database import Document
        doc = Document(
            filename="AKP.docx",
            file_type="docx",
            file_path=test_file
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        print(f"✓ 文档记录创建成功 (ID: {doc.id})")

        # 处理文档
        print("  处理中...")
        chunk_count = await processor.process_document(test_file, doc.id)
        print(f"✓ 文档处理成功，生成 {chunk_count} 个 chunks")

        db.close()

    except Exception as e:
        print(f"✗ 文档处理失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_upload())
