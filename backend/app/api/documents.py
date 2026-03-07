from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Document, DocumentIntent
from app.services.document_processor import DocumentProcessor
from app.services.llm_service import QwenLLMService
from app.services.vector_store import VectorStore
from app.config import get_settings
import os
import shutil

router = APIRouter()
settings = get_settings()

llm_service = QwenLLMService(settings.qwen_api_key)
vector_store = VectorStore(dimension=1024)

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), intent_ids: str = "", db: Session = Depends(get_db)):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    file_path = f"data/uploads/{file.filename}"
    os.makedirs("data/uploads", exist_ok=True)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = Document(
        filename=file.filename,
        file_type=file.filename.split('.')[-1],
        file_path=file_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    if intent_ids:
        for intent_id in intent_ids.split(','):
            db.add(DocumentIntent(document_id=doc.id, intent_id=int(intent_id)))
        db.commit()

    processor = DocumentProcessor(llm_service, vector_store, db)
    chunk_count = await processor.process_document(file_path, doc.id)

    return {"id": doc.id, "filename": file.filename, "chunks": chunk_count}

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [{"id": d.id, "filename": d.filename, "processed": d.processed, "chunk_count": d.chunk_count, "access_count": d.access_count} for d in docs]

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    db.delete(doc)
    db.commit()
    return {"ok": True}
