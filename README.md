# 🧠 IntelliKnow KMS

**Gen AI-Powered Knowledge Management System**

A production-ready KMS that addresses enterprise pain points: fragmented information, inefficient knowledge retrieval, and siloed communication channels. Built in 7 days as a Tech Lead interview case study.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/alexqiao/intelliknow-kms)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ Features

- 🤖 **Multi-Channel Access**: Query knowledge via Telegram and Slack bots
- 📚 **Smart Document Processing**: PDF and DOCX support with AI-powered parsing
- 🎯 **Intent Classification**: Automatic categorization (HR, Legal, Finance, General)
- 🔍 **Semantic Search**: FAISS vector database for accurate retrieval
- 🧠 **Dual LLM Support**: Environment-aware switching (Qwen for local dev, Gemini for production)
- 📊 **Admin Dashboard**: Streamlit-based management interface
- 📈 **Analytics**: Query tracking, classification accuracy, document access stats
- ⚡ **Fast Response**: <3 second end-to-end latency

---

## 🎯 Problem Statement

**Enterprise Challenge**: Organizations struggle with:

1. Knowledge scattered across multiple documents and systems
2. Employees wasting time searching for information
3. Communication tools (Telegram, Slack) disconnected from knowledge bases

**Solution**: IntelliKnow KMS provides:

- Unified knowledge base built from uploaded documents
- Direct access via existing communication tools
- AI-powered intent routing for accurate, context-aware responses

---

## 🏗️ Architecture

![ArchitectureMap.png](/Users/alexsqiao/Documents/github/aia/intelliknow-kms/docs/ArchitectureMap.png)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Qwen API key from [DashScope](https://dashscope.aliyun.com/) (for local development)
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) (for production deployment)
- Aliyun Access Key ID & Secret (Required for cloud-based Document Mind parsing)
- (Optional) Telegram Bot Token
- (Optional) Slack App credentials

### Installation

```bash
# Clone repository
git clone https://github.com/alexqiao/intelliknow-kms.git
cd intelliknow-kms

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)

# Initialize database and default intents
cd ..
python init_intents.py
python migrate_db.py
python migrate_file_size.py

# Run backend
cd backend
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Dashboard Setup

```bash
# In a new terminal
cd dashboard
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000  # On Windows: set BACKEND_URL=http://localhost:8000
streamlit run app.py
```

Dashboard will be available at `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables

Create `backend/.env` file with the following:

```bash
# LLM Provider Configuration
LLM_PROVIDER=qwen                    # Use 'qwen' for local dev, 'gemini' for production
QWEN_API_KEY=sk-your-qwen-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Aliyun Document Mind API (for advanced document parsing)
ALIYUN_ACCESS_KEY_ID=your-aliyun-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-aliyun-access-key-secret

# Optional: Telegram Bot (if using Telegram integration)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-telegram-chat-id

# Optional: Slack Bot (if using Slack integration)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret

# Database (default: SQLite)
DATABASE_URL=sqlite:///./data/intelliknow.db
```

### Getting API Keys

#### 1. Qwen API Key (For Local Development)

1. Visit [DashScope](https://dashscope.aliyun.com/)
2. Register/login with Aliyun account
3. Navigate to "API Key Management"
4. Create new API key
5. Copy the key (starts with `sk-`)

**Free Tier**: 1M tokens/month for development

#### 2. Gemini API Key (For Production Deployment)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the generated key

**Free Tier**: Generous quota for testing and small-scale production

---

## 🤖 Frontend Integration Guide

### Option 1: Telegram Bot Setup

#### Step 1: Create Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to set bot name and username
4. Copy the Bot Token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### Step 2: Get Your Chat ID

1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id":123456789}` in the response
4. Copy the chat ID number

#### Step 3: Configure in Dashboard

1. Open dashboard at `http://localhost:8501`
2. Navigate to "Frontend Integration" page
3. Select "Telegram" tab
4. Enter Bot Token and Admin Chat ID
5. Click "Save & Test"
6. You should receive a "✅ Connection Successful!" message in Telegram

#### Step 4: Set Webhook (for production deployment)

After deploying to cloud:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-backend-url.com/webhook/telegram"
```

---

### Option 2: Slack Bot Setup

#### Step 1: Create Slack App

1. Visit [Slack API](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Enter App Name (e.g., "IntelliKnow KMS") and select workspace
4. Click "Create App"

#### Step 2: Configure Bot Permissions

1. In app settings, go to "OAuth & Permissions"
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add these scopes:
   - `chat:write` (send messages)
   - `channels:history` (read channel messages)
   - `groups:history` (read private channel messages)
   - `im:history` (read direct messages)
4. Scroll up and click "Install to Workspace"
5. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

#### Step 3: Enable Event Subscriptions

1. Go to "Event Subscriptions" in app settings
2. Toggle "Enable Events" to ON
3. Enter Request URL: `https://your-backend-url.com/webhook/slack`
   - For local testing, use [ngrok](https://ngrok.com/): `ngrok http 8000`
4. Under "Subscribe to bot events", add:
   - `message.channels`
   - `message.groups`
   - `message.im`
5. Click "Save Changes"

#### Step 4: Get Signing Secret

1. Go to "Basic Information" in app settings
2. Scroll to "App Credentials"
3. Copy the "Signing Secret"

#### Step 5: Configure in Dashboard

1. Open dashboard at `http://localhost:8501`
2. Navigate to "Frontend Integration" page
3. Select "Slack" tab
4. Enter Bot Token and Signing Secret
5. Click "Save & Test"
6. You should receive a "✅ Connection Successful!" message in Slack

#### Step 6: Invite Bot to Channel

1. In Slack, go to the channel where you want to use the bot
2. Type `/invite @IntelliKnow KMS` (or your bot name)
3. The bot will now respond to messages in that channel

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

---

## 📚 Usage Guide

### 1. Upload Documents

1. Open dashboard → "Knowledge Base" page
2. Click "Upload Document" section
3. Select PDF or DOCX file
4. Choose intent space(s) to associate (HR, Legal, Finance)
5. Click "Upload"
6. Wait for processing (status will show "Processed")

### 2. Query via Telegram/Slack

Simply send a message to your bot:

```
User: What is the vacation policy?
Bot: According to the HR Policy document, employees receive:
- 0-1 years: 10 vacation days
- 2-3 years: 15 vacation days
- 4+ years: 20 vacation days

[Source: HR_Policy.pdf]
```

### 3. Manage Intent Spaces

1. Dashboard → "Intent Configuration"
2. View existing intents (HR, Legal, Finance, General)
3. Click "Create New Intent" to add custom categories
4. Edit keywords to improve classification accuracy

### 4. View Analytics

1. Dashboard → "Analytics"
2. View query statistics, intent distribution, response times
3. Export query logs as CSV for further analysis
4. Monitor most accessed documents

---

## 🛠️ Tech Stack

| Component        | Technology                                    | Purpose                          |
| ---------------- | --------------------------------------------- | -------------------------------- |
| Backend API      | FastAPI                                       | REST API and webhook handlers    |
| Database         | SQLite                                        | Metadata storage                 |
| Vector Store     | FAISS                                         | Semantic search                  |
| LLM              | Qwen API (local) / Gemini API (production)    | Embeddings & response generation |
| Document Parsing | Aliyun Document Mind API + PyPDF2/python-docx | Text extraction with fallback    |
| Admin UI         | Streamlit                                     | Management dashboard             |
| Telegram         | python-telegram-bot                           | Bot integration                  |
| Slack            | slack-sdk                                     | Bot integration                  |

---

## 📖 API Documentation

### Core Endpoints

#### Query API

```bash
POST /api/query
Content-Type: application/json

{
  "query": "What is the vacation policy?",
  "source": "telegram",
  "user_id": "123456"
}

Response:
{
  "intent": "HR",
  "confidence": 0.92,
  "response": "According to the HR Policy...",
  "response_time_ms": 1850
}
```

#### Document Upload

```bash
POST /api/documents/upload
Content-Type: multipart/form-data

file: <PDF or DOCX file>
intent_ids: "1,2"  # Comma-separated intent IDs

Response:
{
  "id": 5,
  "filename": "HR_Policy.pdf",
  "chunks": 24
}
```

#### List Documents

```bash
GET /api/documents

Response:
[
  {
    "id": 1,
    "filename": "HR_Policy.pdf",
    "processed": true,
    "chunk_count": 24,
    "access_count": 15
  }
]
```

Full API documentation available at `http://localhost:8000/docs` (Swagger UI)

---

## 🧪 Testing

### Run End-to-End Tests

```bash
cd backend
python -m pytest tests/test_e2e.py -v
```

### Test Query Flow

```bash
python test_query.py
```

### Performance Testing

```bash
python backend/tests/test_performance.py
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Cloud

**Backend (Render)**:

1. Push code to GitHub
2. Create Web Service on [Render](https://render.com)
3. Connect repository, set root directory to `backend`
4. Add environment variables
5. Deploy

**Dashboard (Streamlit Cloud)**:

1. Visit [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect GitHub repository
3. Set main file to `dashboard/app.py`
4. Add `BACKEND_URL` environment variable
5. Deploy

---

## 🔧 Troubleshooting

### Common Issues

**1. "Database not found" error**

```bash
# Ensure data directory exists
mkdir -p backend/data
python init_intents.py
```

**2. "FAISS dimension mismatch"**

```bash
# Delete existing index and rebuild
rm -rf backend/data/faiss_index/*
python backend/rebuild_faiss.py
# Re-upload documents via dashboard
```

**3. "Telegram webhook not responding"**

- Check bot token is correct
- Verify webhook URL is publicly accessible (use ngrok for local testing)
- Check backend logs: `uvicorn app.main:app --log-level debug`

**4. "Slack events not received"**

- Verify Request URL in Slack app settings shows ✓ verified
- Check signing secret matches .env file
- Ensure bot is invited to the channel

**5. "Response time >3 seconds"**

- Check Qwen API latency
- Verify FAISS index is loaded (check logs)
- Consider reducing chunk retrieval count (default: 5)

---

## 📊 Project Structure

```
intelliknow-kms/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # SQLAlchemy models
│   │   ├── api/               # API endpoints
│   │   │   ├── webhooks.py    # Telegram/Slack webhooks
│   │   │   ├── query.py       # Query processing
│   │   │   ├── documents.py   # Document management
│   │   │   ├── intents.py     # Intent management
│   │   │   └── config.py      # Frontend config API
│   │   ├── services/          # Business logic
│   │   │   ├── orchestrator.py       # Query orchestration
│   │   │   ├── document_processor.py # Document parsing
│   │   │   ├── vector_store.py       # FAISS operations
│   │   │   ├── llm_service.py        # Qwen API wrapper
│   │   │   ├── telegram_client.py    # Telegram integration
│   │   │   └── slack_client.py       # Slack integration
│   │   └── utils/             # Utilities
│   │       ├── formatters.py  # Response formatting
│   │       └── security.py    # Input sanitization
│   ├── data/                  # Data storage
│   │   ├── intelliknow.db     # SQLite database
│   │   ├── faiss_index/       # Vector index
│   │   └── uploads/           # Uploaded documents
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
│
├── dashboard/                 # Streamlit admin UI
│   ├── app.py                # Main dashboard
│   ├── pages/                # Multi-page app
│   │   ├── 1_Frontend_Integration.py
│   │   ├── 2_Knowledge_Base.py
│   │   ├── 3_Intent_Config.py
│   │   └── 4_Analytics.py
│   └── requirements.txt
│
├── docs/                     # Documentation
│   ├── README.md            # Full documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── AI_USAGE_REFLECTION.md  # AI tools reflection
│
├── sample_docs/              # Sample documents
├── init_intents.py          # Database initialization
└── README.md                # This file
```

---

## 📝 Documentation

- **[Full Documentation](docs/TechnicalDocumentation.md)** - Comprehensive project documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Cloud and local deployment
- **[AI Usage Reflection](docs/AI_USAGE_REFLECTION.md)** - AI tools strategy and impact

---

## 🤝 Contributing

This is a case study project for interview purposes. For questions or feedback, please open an issue.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Qwen (通义千问)** by Alibaba Cloud for LLM capabilities
- **FastAPI** for the excellent web framework
- **Streamlit** for rapid dashboard development
- **FAISS** by Meta for efficient vector search

---

## 📧 Contact

For questions about this project, please open an issue on GitHub.
