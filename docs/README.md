# IntelliKnow KMS

Knowledge Management System powered by Gen AI with multi-channel access via Telegram and Slack.

## Features

- 🤖 **Multi-Channel Access**: Query knowledge base via Telegram and Slack
- 📚 **Document Processing**: Support for PDF and DOCX files
- 🎯 **Intent Classification**: Automatic categorization (HR, Legal, Finance)
- 🔍 **Semantic Search**: FAISS-powered vector search
- 🧠 **AI-Powered**: Qwen LLM for embeddings and responses
- 📊 **Analytics Dashboard**: Track queries and performance

## Quick Start

### Prerequisites

- Python 3.11+
- Qwen API key (from https://dashscope.aliyun.com/)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

### Dashboard Setup

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

## API Endpoints

- `POST /webhook/telegram` - Telegram webhook
- `POST /webhook/slack` - Slack webhook
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/intents` - List intents
- `POST /api/query` - Direct query API

## Architecture

```
User (Telegram/Slack) → Webhook → Query Orchestrator
                                        ↓
                            Intent Classifier (Qwen)
                                        ↓
                            Vector Search (FAISS)
                                        ↓
                            Response Generator (Qwen)
```

## License

MIT
