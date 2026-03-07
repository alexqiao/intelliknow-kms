from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, QueryLog
from app.services.orchestrator import QueryOrchestrator
from app.services.llm_service import QwenLLMService
from app.services.vector_store import VectorStore
from app.config import get_settings
from pydantic import BaseModel

router = APIRouter()
settings = get_settings()

llm_service = QwenLLMService(settings.qwen_api_key)
vector_store = VectorStore(dimension=1024)

class QueryRequest(BaseModel):
    query: str
    source: str = "api"
    user_id: str = "anonymous"

@router.post("/query")
async def process_query(req: QueryRequest, db: Session = Depends(get_db)):
    orchestrator = QueryOrchestrator(llm_service, vector_store, db)
    result = await orchestrator.process_query(req.query, req.source, req.user_id)
    return result

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    logs = db.query(QueryLog).all()
    by_intent = {}
    by_source = {}
    for log in logs:
        intent = log.classified_intent or "Unknown"
        by_intent[intent] = by_intent.get(intent, 0) + 1
        source = log.frontend_source or "unknown"
        by_source[source] = by_source.get(source, 0) + 1

    rt_values = [l.response_time_ms for l in logs if l.response_time_ms]

    return {
        "total_queries": len(logs),
        "by_intent": by_intent,
        "by_source": by_source,
        "avg_response_time": sum(rt_values) / len(rt_values) if rt_values else 0,
        "max_response_time": max(rt_values) if rt_values else 0,
        "min_response_time": min(rt_values) if rt_values else 0,
        "queries_within_3s": sum(1 for v in rt_values if v <= 3000),
    }

@router.get("/query_logs")
async def get_query_logs(db: Session = Depends(get_db)):
    logs = db.query(QueryLog).order_by(QueryLog.timestamp.desc()).all()
    return [{
        "id": l.id,
        "query_text": l.query_text,
        "frontend_source": l.frontend_source,
        "user_id": l.user_id,
        "classified_intent": l.classified_intent,
        "confidence_score": l.confidence_score,
        "response_text": l.response_text,
        "response_time_ms": l.response_time_ms,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None
    } for l in logs]
