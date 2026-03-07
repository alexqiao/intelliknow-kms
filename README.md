# 🧠 IntelliKnow KMS

**Knowledge Management System powered by Gen AI**

A 7-day case study project demonstrating enterprise knowledge management with multi-channel access via Telegram and Slack.

## ✨ Features

- 🤖 **Multi-Channel Access**: Query via Telegram and Slack bots
- 📚 **Document Processing**: PDF and DOCX support with automatic chunking
- 🎯 **Intent Classification**: AI-powered categorization (HR, Legal, Finance)
- 🔍 **Semantic Search**: FAISS vector database for accurate retrieval
- 🧠 **Qwen LLM Integration**: Embeddings and response generation
- 📊 **Management Dashboard**: Streamlit-based admin interface
- 📈 **Analytics**: Query tracking and performance metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Qwen API key from [DashScope](https://dashscope.aliyun.com/)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd intelliknow-kms

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database and run
uvicorn app.main:app --reload
```

### Dashboard

```bash
cd dashboard
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
streamlit run app.py
```

Visit http://localhost:8501 for the admin dashboard.

## 📖 Documentation

- [README](docs/README.md) - Full documentation
- [DEPLOYMENT](docs/DEPLOYMENT.md) - Deployment guide
- [AI_USAGE_REFLECTION](docs/AI_USAGE_REFLECTION.md) - AI tools reflection

## 🏗️ Architecture

```
Telegram/Slack → Webhook → Query Orchestrator
                                ↓
                    Intent Classifier (Qwen)
                                ↓
                    Vector Search (FAISS)
                                ↓
                    Response Generator (Qwen)
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, FAISS
- **AI**: Qwen API (通义千问)
- **Frontend**: Streamlit
- **Integrations**: Telegram Bot API, Slack SDK
- **Database**: SQLite

## 📝 License

MIT
