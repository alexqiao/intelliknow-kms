# IntelliKnow KMS - Technical Documentation

## System Overview

IntelliKnow KMS is a Gen AI-powered Knowledge Management System designed to address enterprise knowledge retrieval challenges. It integrates with common communication tools (Telegram, Slack), automatically processes uploaded documents, and uses AI-powered intent classification to route queries to the correct knowledge domain.

## Core Modules

### 1. Query Orchestrator (`backend/app/services/orchestrator.py`)

The central component that coordinates the entire query processing pipeline:

1. **Intent Classification**: Uses Qwen LLM to classify user queries into predefined categories (HR, Legal, Finance, General) with a configurable confidence threshold (default: 70%)
2. **Document Retrieval**: Performs semantic search via FAISS, filtered by classified intent
3. **Response Generation**: Uses RAG (Retrieval-Augmented Generation) to generate cited responses
4. **Fallback Mechanism**: If intent-specific search yields no results, falls back to global search

### 2. Document Processor (`backend/app/services/document_processor.py`)

Handles the complete document ingestion pipeline:
- **Text Extraction**: PyPDF2 for PDFs, python-docx for DOCX files
- **Chunking**: RecursiveCharacterTextSplitter (500 chars/chunk, 50 overlap)
- **Embedding**: Qwen text-embedding-v3 (1024 dimensions)
- **Storage**: FAISS index + SQLite metadata

### 3. Vector Store (`backend/app/services/vector_store.py`)

FAISS-based vector storage with:
- IndexFlatL2 for exact nearest-neighbor search
- Metadata mapping (faiss_id → content + doc_id)
- Disk persistence (auto-save/load)

### 4. LLM Service (`backend/app/services/llm_service.py`)

Qwen API wrapper using OpenAI-compatible interface:
- Chat completion (qwen-plus model)
- Text embeddings (text-embedding-v3, 1024 dimensions)
- Async operations for non-blocking I/O

### 5. Frontend Integrations

- **Telegram** (`backend/app/services/telegram_client.py`): Webhook-based message handling
- **Slack** (`backend/app/services/slack_client.py`): Event subscription with signature verification

### Slack Integration Troubleshooting

**Issue 1: Cannot send messages to the bot**

If the UI shows "Sending messages to this app has been turned off":
- Go to Slack API Dashboard (api.slack.com/apps) and select your app
- Navigate to "App Home" under "Features"
- Scroll to "Show Tabs" section
- Enable the "Messages Tab" toggle
- **Critical**: Check "Allow users to send Slash commands and messages from the messages tab"
- Refresh Slack client - message input will unlock immediately

**Issue 2: Finding the Admin Channel ID**

To get the Channel ID for dashboard configuration:
- Log into Slack web version in a browser
- Navigate to the channel or DM with the bot
- Check the URL bar (e.g., `app.slack.com/client/T1234567/C987654321`)
- The final string starting with 'C' (channels) or 'U' (user DMs) is your Channel ID

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

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhook/telegram` | Telegram webhook handler |
| POST | `/webhook/slack` | Slack webhook handler |
| POST | `/api/query` | Direct query API |
| POST | `/api/documents/upload` | Upload document (PDF/DOCX) |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/{id}` | Delete document |
| GET | `/api/intents` | List all intents |
| POST | `/api/intents` | Create intent |
| PUT | `/api/intents/{id}` | Update intent |
| DELETE | `/api/intents/{id}` | Delete intent |
| GET | `/api/analytics` | Get analytics data |
| GET | `/api/query_logs` | Get query history |
| GET | `/api/config/frontend/{platform}` | Get frontend config |
| POST | `/api/config/frontend` | Save frontend config |
| POST | `/api/config/frontend/{platform}/test` | Test frontend connection |

Full API documentation: `http://localhost:8000/docs` (Swagger UI)

## Data Flow

### Query Flow
```
User Message → Webhook/API → Orchestrator
  → Intent Classification (Qwen LLM + DB intents)
  → Semantic Retrieval (FAISS + DocumentIntent filter)
  → Response Generation (Qwen RAG)
  → Format Response (platform-specific)
  → Return to User + Log to DB
```

### Document Upload Flow
```
File Upload → Save to disk → Extract text (PDF/DOCX)
  → Chunk text (500 chars, 50 overlap)
  → Generate embeddings (Qwen text-embedding-v3)
  → Store in FAISS index + SQLite metadata
  → Associate with intent spaces
```

## Configuration

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment and configuration instructions.

## Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| End-to-end response time | ≤ 3 seconds | ~1.5-2.5 seconds |
| Intent classification accuracy | ≥ 70% | ~85% |
| Document processing | < 30 seconds per doc | ~10-20 seconds |

## Security

- Input sanitization on all user queries
- Slack webhook signature verification
- Credential masking in dashboard (last 4 digits only)
- Database-backed credential storage
- No hardcoded secrets in code
