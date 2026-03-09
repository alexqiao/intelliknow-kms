from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Document, DocumentIntent
from app.services.document_processor import DocumentProcessor
from app.dependencies import vector_store_instance, llm_service_instance
from app.config import get_settings
import os
import shutil
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), intent_ids: str = "", db: Session = Depends(get_db)):
    try:
        logger.info(f"Upload started: {file.filename}, content_type: {file.content_type}")

        if not file.filename.endswith(('.pdf', '.docx')):
            raise HTTPException(400, "Only PDF and DOCX files are supported")

        file_path = f"data/uploads/{file.filename}"
        os.makedirs("data/uploads", exist_ok=True)

        # Save file and get size
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_size = os.path.getsize(file_path)
        logger.info(f"File saved: {file_path}, size: {file_size} bytes")

        doc = Document(
            filename=file.filename,
            file_type=file.filename.split('.')[-1],
            file_path=file_path,
            file_size=file_size
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info(f"DB record created: doc_id={doc.id}")

        if intent_ids:
            for intent_id in intent_ids.split(','):
                existing = db.query(DocumentIntent).filter(
                    DocumentIntent.document_id == doc.id,
                    DocumentIntent.intent_id == int(intent_id)
                ).first()
                if not existing:
                    db.add(DocumentIntent(document_id=doc.id, intent_id=int(intent_id)))
            db.commit()
        else:
            # Auto-classify document intent
            from app.database import Intent
            intents = db.query(Intent).all()
            intent_list = "\n".join([f"- {i.name} (id={i.id}): {i.description}" for i in intents])

            prompt = f"""Analyze the filename and determine which intent category this document belongs to:

{intent_list}

Filename: {file.filename}

Respond with only the intent ID number (e.g., "2" for Legal)."""

            try:
                response = await llm_service_instance.chat_completion([{"role": "user", "content": prompt}])
                intent_id = int(response.strip())
                existing = db.query(DocumentIntent).filter(
                    DocumentIntent.document_id == doc.id,
                    DocumentIntent.intent_id == intent_id
                ).first()
                if not existing:
                    db.add(DocumentIntent(document_id=doc.id, intent_id=intent_id))
                    db.commit()
                    logger.info(f"Auto-classified to intent_id={intent_id}")
            except Exception as e:
                db.rollback()
                logger.warning(f"Failed to auto-classify: {e}")

        logger.info(f"Starting document processing: doc_id={doc.id}")
        processor = DocumentProcessor(llm_service_instance, vector_store_instance, db)
        chunk_count = await processor.process_document(file_path, doc.id)
        logger.info(f"Processing complete: {chunk_count} chunks")

        return {"id": doc.id, "filename": file.filename, "chunks": chunk_count}

    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [{
        "id": d.id,
        "filename": d.filename,
        "processed": d.processed,
        "chunk_count": d.chunk_count,
        "access_count": d.access_count,
        "file_size": d.file_size
    } for d in docs]

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    vector_store_instance.remove_document(doc_id)
    db.delete(doc)
    db.commit()
    return {"ok": True}
