from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Intent(Base):
    __tablename__ = "intents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    keywords = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer, default=0)  # File size in bytes
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    access_count = Column(Integer, default=0)

class DocumentIntent(Base):
    __tablename__ = "document_intents"
    document_id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    intent_id = Column(Integer, ForeignKey("intents.id"), primary_key=True)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    faiss_id = Column(Integer)

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    frontend_source = Column(String(50))
    user_id = Column(String(100))
    classified_intent = Column(String(100))
    confidence_score = Column(Float)
    response_text = Column(Text)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class FrontendConfig(Base):
    __tablename__ = "frontend_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), unique=True, nullable=False)
    enabled = Column(Boolean, default=False)
    credentials = Column(Text, nullable=False)
    status = Column(String(50), default="inactive")
    created_at = Column(DateTime, default=datetime.utcnow)

os.makedirs("data", exist_ok=True)
engine = create_engine("sqlite:///data/intelliknow.db")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    if session.query(Intent).count() == 0:
        defaults = [
            Intent(name="HR", description="Human Resources policies, benefits, vacation", keywords="vacation,leave,benefits,policy"),
            Intent(name="Legal", description="Legal terms, contracts, compliance", keywords="legal,contract,terms,compliance"),
            Intent(name="Finance", description="Financial policies, expenses, budgets", keywords="finance,expense,budget,payment")
        ]
        session.add_all(defaults)
        session.commit()
    session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
