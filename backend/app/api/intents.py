from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Intent
from pydantic import BaseModel

router = APIRouter()

class IntentCreate(BaseModel):
    name: str
    description: str
    keywords: str = ""

@router.get("/intents")
async def list_intents(db: Session = Depends(get_db)):
    intents = db.query(Intent).all()
    return [{"id": i.id, "name": i.name, "description": i.description, "keywords": i.keywords} for i in intents]

@router.post("/intents")
async def create_intent(intent: IntentCreate, db: Session = Depends(get_db)):
    new_intent = Intent(name=intent.name, description=intent.description, keywords=intent.keywords)
    db.add(new_intent)
    db.commit()
    db.refresh(new_intent)
    return {"id": new_intent.id, "name": new_intent.name}

@router.put("/intents/{intent_id}")
async def update_intent(intent_id: int, intent: IntentCreate, db: Session = Depends(get_db)):
    existing = db.query(Intent).filter(Intent.id == intent_id).first()
    if not existing:
        raise HTTPException(404, "Intent not found")
    existing.name = intent.name
    existing.description = intent.description
    existing.keywords = intent.keywords
    db.commit()
    return {"id": existing.id, "name": existing.name}

@router.delete("/intents/{intent_id}")
async def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.id == intent_id).first()
    if not intent:
        raise HTTPException(404, "Intent not found")
    db.delete(intent)
    db.commit()
    return {"ok": True}
