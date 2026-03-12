# IntelliKnow KMS - Technical Documentation

## System Overview

IntelliKnow KMS is a Gen AI-powered Knowledge Management System designed to address enterprise knowledge retrieval challenges. It integrates with common communication tools (Telegram, Slack), automatically processes uploaded documents, and uses AI-powered intent classification to route queries to the correct knowledge domain.The system is highly optimized for resource-constrained serverless environments (e.g., Render free/starter tiers).



![ArchitectureMap.png](/Users/alexsqiao/Documents/github/aia/intelliknow-kms/docs/ArchitectureMap.png)

## Core Modules

### 1. Query Orchestrator (`backend/app/services/orchestrator.py`)

The central component that coordinates the entire query processing pipeline:

1. **Intent Classification**: Uses LLM to classify user queries into predefined categories (HR, Legal, Finance, General) with a configurable confidence threshold (default: 70%)
2. **Document Retrieval**: Performs semantic search via FAISS, filtered by classified intent. Uses doc_id directly from FAISS metadata to prevent ID desync issues after document deletion.
3. **Response Generation**: Uses RAG (Retrieval-Augmented Generation) to generate cited responses
4. **Fallback Mechanism**: If intent-specific search yields no results, falls back to global search

**Critical Fix**: Retrieval now bypasses DocumentChunk table and uses doc_id from FAISS metadata directly, preventing FAISS ID desync after document deletion and re-indexing.

### 2. Document Processor (`backend/app/services/document_processor.py`)

Implements a **Dual-Pipeline Architecture** for enterprise-grade document processing:

**Primary Pipeline: Aliyun Document Mind API**

- High-fidelity Markdown extraction with perfect table/layout preservation
- Async polling mechanism (60s timeout) for cloud-based OCR/layout analysis
- Offloads compute-intensive operations to avoid Render's 512MB RAM constraints

**Fallback Pipeline: Local Extraction**

- PyPDF2 for PDFs, python-docx for DOCX files
- Ensures 100% uptime when cloud API is unavailable or times out
- Graceful degradation without service interruption

**Post-Extraction Processing:**

- **Chunking**: RecursiveCharacterTextSplitter (500 chars/chunk, 50 overlap)
- **Embedding**: Environment-aware (Qwen 1024-dim or Gemini 3072-dim)
- **Storage**: FAISS index + SQLite metadata

### 3. Vector Store (`backend/app/services/vector_store.py`)

FAISS-based vector storage with **dynamic dimension support**:

- IndexFlatL2 for exact nearest-neighbor search
- Metadata mapping (faiss_id → content + doc_id)
- Disk persistence (auto-save/load)
- **Environment-aware dimensions**: Qwen (1024-dim) or Gemini (3072-dim)

### 4. LLM Service (`backend/app/services/llm_service.py`)

**Environment-Aware LLM Architecture** using Factory Pattern:

**Qwen Provider** (Local Development in China):

- Chat: qwen-turbo model
- Embeddings: text-embedding-v3 (1024 dimensions)
- Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1

**Gemini Provider** (Render Deployment in US):

- Chat: gemini-2.5-flash-lite model
- Embeddings: gemini-embedding-001 (3072 dimensions)
- Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
- **Purpose**: Mitigates cross-ocean latency (reduces response time from >4000ms to <2000ms)

Both providers use **AsyncOpenAI** client for non-blocking event loop execution, enabling true concurrent processing with FastAPI's async capabilities.

### 5. Frontend Integrations

- **Telegram** (`backend/app/services/telegram_client.py`): Webhook-based message handling
- **Slack** (`backend/app/services/slack_client.py`): Event subscription with signature verification

### 6. Admin Dashboard (`dashboard/`)

Streamlit multi-page app with 5 screens:

- **Dashboard**: Overview statistics (queries, response time, intents)
- **Frontend Integration**: Credential management, connection testing
- **Knowledge Base**: Document upload, library management
- **Intent Configuration**: Intent CRUD, classification logs, accuracy metrics
- **Analytics**: Charts, response time analysis, CSV export

## Database Schema

```sql
-- Core tables
intents (id, name, description, keywords, created_at)
documents (id, filename, file_type, file_path, file_size, upload_date, processed, chunk_count, access_count)
document_intents (document_id, intent_id)  -- Many-to-many association
document_chunks (id, document_id, chunk_index, content, faiss_id)
query_logs (id, query_text, frontend_source, user_id, classified_intent, confidence_score, response_text, response_time_ms, timestamp)
frontend_configs (id, platform, enabled, credentials, status, created_at)
```

## API Endpoints

Full API documentation: `https://intelliknow-kms-api-9e88.onrender.com/docs` (Swagger UI)

## Data Flow

### Query Flow

```
User Message → Webhook/API → Orchestrator
  → Intent Classification (Qwen/Gemini LLM + DB intents)
  → Semantic Retrieval (FAISS + DocumentIntent filter)
  → Response Generation (Qwen/Gemini RAG)
  → Format Response (platform-specific)
  → Return to User + Log to DB
```

### Document Upload Flow

```
File Upload → Save to disk → Aliyun Document Mind API (Primary)
  → [If success] Extract Markdown with tables/layouts
  → [If timeout/fail] Fallback to local PyPDF2/python-docx
  → Chunk text (500 chars, 50 overlap)
  → Generate embeddings (Qwen 1024-dim or Gemini 3072-dim)
  → Store in FAISS index + SQLite metadata
  → Associate with intent spaces
```

## Configuration

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment and configuration instructions.

## Performance Targets

| Metric                         | Target      | Measured         |
| ------------------------------ | ----------- | ---------------- |
| End-to-end response time       | ≤ 3 seconds | ~1.5-2.5 seconds |
| End-to-end Accuracy            | N/A         | **～94%**         |
| Intent classification accuracy | ≥ 70%       | **~94%**         |

## Security

- Input sanitization on all user queries
- Slack webhook signature verification
- Credential masking in dashboard (last 4 digits only)
- Database-backed credential storage
- No hardcoded secrets in code

## Data Integrity & Availability

**Critical Fixes Implemented:**

1. **FAISS ID Desync Prevention**: The orchestrator now retrieves documents using `doc_id` directly from FAISS metadata instead of joining via `faiss_id` from DocumentChunk table. This prevents ID mismatches after document deletion triggers FAISS re-indexing.

2. **Orphan Data Cleanup**: Document deletion endpoint now explicitly deletes associated DocumentChunk and DocumentIntent records before removing the Document record, preventing orphaned data in the database.

3. **Cold Start Mitigation**: Implemented a `/health` endpoint supporting both `GET` and `HEAD` methods. This integrates seamlessly with UptimeRobot's free tier to ping the container every 5 minutes, keeping the TCP connection pool warm and preventing the serverless instance from sleeping.
