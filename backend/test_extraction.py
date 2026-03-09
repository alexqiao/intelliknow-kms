import asyncio
from app.dependencies import llm_service_instance

async def test_extraction():
    file_path = "data/uploads/HR_Policy.pdf"

    print(f"Testing extraction on: {file_path}")

    try:
        content = await llm_service_instance.extract_document_content(file_path)
        print(f"\n✅ Extraction successful!")
        print(f"Content length: {len(content)} characters")
        print(f"\nFirst 500 characters:\n{content[:500]}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_extraction())
