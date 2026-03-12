# Deployment Guide - IntelliKnow KMS

## Table of Contents

- [Local Deployment](#local-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Webhook Configuration](#webhook-configuration)
- [Environment Variables](#environment-variables)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites

- Python 3.11+
- Qwen API Key ([Get it here](https://dashscope.aliyun.com/))
- (Optional) Telegram Bot Token / Slack App credentials

### Step 1: Backend Setup

```bash
# Clone repository
git clone https://github.com/alexqiao/intelliknow-kms.git
cd intelliknow-kms

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)
```

### Step 2: Initialize Database

```bash
# From project root
cd ..
python init_intents.py    # Creates default intents (HR, Legal, Finance)
python migrate_db.py      # Applies database migrations
python migrate_file_size.py  # Adds file size tracking
```

### Step 3: Start Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify: Open `http://localhost:8000/docs` - you should see the Swagger API documentation.

### Step 4: Dashboard Setup

```bash
# In a new terminal
cd dashboard
pip install -r requirements.txt

# Set backend URL
export BACKEND_URL=http://localhost:8000  # On Windows: set BACKEND_URL=http://localhost:8000

# Start dashboard
streamlit run app.py
```

Verify: Open `http://localhost:8501` - you should see the IntelliKnow dashboard.

### Step 5: Local Webhook Testing (Optional)

For testing Telegram/Slack webhooks locally, use [ngrok](https://ngrok.com/):

```bash
# Install ngrok
# macOS: brew install ngrok
# Or download from https://ngrok.com/download

# Expose local backend
ngrok http 8000
```

Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`) and use it as the webhook URL.

---

## Cloud Deployment

### Backend on Render

#### Step 1: Prepare Repository

Ensure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Create Render Account

1. Visit [https://render.com](https://render.com)
2. Sign up with GitHub account

#### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `alexqiao/intelliknow-kms`
3. Configure settings:

| Setting        | Value                                              |
| -------------- | -------------------------------------------------- |
| Name           | `intelliknow-kms-api`                              |
| Root Directory | `backend`                                          |
| Runtime        | Python 3                                           |
| Build Command  | `pip install -r requirements.txt`                  |
| Start Command  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type  | Free (or Starter for persistent disk)              |

#### Step 4: Configure Environment Variables

In Render dashboard → Environment:

```
QWEN_API_KEY=your_qwen_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
DATABASE_URL=sqlite:///./data/intelliknow.db
TELEGRAM_BOT_TOKEN=your_telegram_token
SLACK_BOT_TOKEN=your_slack_token
SLACK_SIGNING_SECRET=your_slack_secret
ALIYUN_ACCESS_KEY_ID=your_aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_aliyun_access_key_secret
```

#### Step 5: Enable Persistent Disk (Recommended)

1. Go to service settings → Disks
2. Add disk:
   - Name: `intelliknow-data`
   - Mount Path: `/opt/render/project/src/data`
   - Size: 1 GB

This ensures database and FAISS index persist across deploys.

#### Step 6: Deploy

Click "Manual Deploy" → "Deploy latest commit"

Wait for build to complete (~2-5 minutes). Your backend URL will be: `https://intelliknow-kms-api.onrender.com`

---

### Dashboard on Streamlit Cloud

#### Step 1: Prepare Streamlit Config

Ensure `dashboard/requirements.txt` includes all dependencies:

```
streamlit==1.30.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
```

#### Step 2: Deploy to Streamlit Cloud

1. Visit [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect GitHub repository: `alexqiao/intelliknow-kms`
4. Configure:

| Setting        | Value                      |
| -------------- | -------------------------- |
| Repository     | `alexqiao/intelliknow-kms` |
| Branch         | `main`                     |
| Main file path | `dashboard/app.py`         |
| Python version | 3.11                       |

5. Add secrets (Settings → Secrets):
   
   ```toml
   BACKEND_URL = "https://intelliknow-kms-api.onrender.com"
   ```

Or use environment variables in Advanced Settings.

6. Click "Deploy"

Your dashboard URL will be: `https://alexqiao-intelliknow-kms-dashboard-app.streamlit.app`

---

## Webhook Configuration

After cloud deployment, update webhook URLs for frontend integrations.

### Telegram Webhook

```bash
# Set webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://intelliknow-kms-api.onrender.com/webhook/telegram"

# Verify webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

Expected response:

```json
{
  "ok": true,
  "result": {
    "url": "https://intelliknow-kms-api.onrender.com/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

### Slack Webhook

1. Go to [Slack API](https://api.slack.com/apps) → Your App
2. Click "Event Subscriptions"
3. Update Request URL to: `https://intelliknow-kms-api.onrender.com/webhook/slack`
4. Wait for verification (Slack sends a challenge request)
5. Ensure "Subscribe to bot events" includes:
   - `message.channels`
   - `message.groups`
   - `message.im`
6. Click "Save Changes"

---

## Verification Checklist

After deployment, verify each component works:

### Backend API

- [ ] Health check: `curl https://your-backend.onrender.com/docs`
- [ ] List intents: `curl https://your-backend.onrender.com/api/intents`
- [ ] List documents: `curl https://your-backend.onrender.com/api/documents`

### Dashboard

- [ ] Homepage loads with statistics
- [ ] "Frontend Integration" page shows connection status
- [ ] "Knowledge Base" page lists documents
- [ ] "Intent Configuration" page lists intents
- [ ] "Analytics" page shows charts

### Telegram Integration

- [ ] Send message to bot → receive response
- [ ] Response contains source citations
- [ ] Response time < 3 seconds
- [ ] Query logged in analytics

### Slack Integration

- [ ] Send message in channel → bot responds
- [ ] Response formatted correctly
- [ ] Response time < 3 seconds
- [ ] Query logged in analytics

### Document Upload

- [ ] Upload PDF via dashboard → processed successfully
- [ ] Upload DOCX via dashboard → processed successfully
- [ ] Document appears in library with chunk count and size
- [ ] Query related to document returns relevant results

### Intent Classification

- [ ] HR query → classified as "HR"
- [ ] Legal query → classified as "Legal"
- [ ] Finance query → classified as "Finance"
- [ ] Unknown query → fallback to "General"

---

## Troubleshooting

### Common Issues

**1. "Database not found" error**

```bash
# Create data directory
mkdir -p backend/data
# Re-initialize
python init_intents.py
```

**2. FAISS dimension mismatch**

```bash
# The system uses 1024-dimensional embeddings (text-embedding-v3)
# If you see dimension errors, delete and rebuild:
rm -rf backend/data/faiss_index/*
# Re-upload documents via dashboard
```

**3. Render deployment: "No module named 'app'"**

- Ensure Root Directory is set to `backend` in Render settings
- Check that `requirements.txt` is in the `backend/` directory

**4. Streamlit Cloud: "BACKEND_URL not found"**

- Add `BACKEND_URL` in Streamlit Cloud → Settings → Secrets:
  
  ```toml
  BACKEND_URL = "https://your-backend.onrender.com"
  ```

**5. Telegram webhook not responding**

- Verify webhook URL is correct: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Check Render logs for errors: Render Dashboard → Logs
- Ensure bot token in .env matches BotFather token

**6. Slack events not received**

- Verify Request URL shows green checkmark in Slack API dashboard
- Check signing secret matches
- Ensure bot is invited to the channel: `/invite @YourBot`

**7. Render free tier cold starts**

- Free tier services spin down after 15 minutes of inactivity
- First request after idle may take 30-60 seconds
- Solution: Upgrade to Starter ($7/month) for always-on service

**8. Response time exceeds 3 seconds**

- Check Gemini API latency (may vary by region)
- Reduce `top_k` in orchestrator from 5 to 3
- Ensure FAISS index is loaded (check logs for "loading index")
