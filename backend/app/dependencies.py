from app.services.vector_store import VectorStore
from app.services.llm_service import get_llm_service
from app.config import get_settings

settings = get_settings()

# Initialize LLM service and VectorStore based on provider
if settings.llm_provider == "gemini":
    llm_service_instance = get_llm_service("gemini", settings)
    vector_store_instance = VectorStore(dimension=3072)
else:
    llm_service_instance = get_llm_service("qwen", settings)
    vector_store_instance = VectorStore(dimension=1024)
