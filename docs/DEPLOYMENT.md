# Deployment Guide

## Local Deployment

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Add your API keys

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Dashboard

```bash
cd dashboard
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
streamlit run app.py
```

## Cloud Deployment

### Backend on Render

1. Create account at https://render.com
2. New Web Service → Connect GitHub repo
3. Settings:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   ```
   QWEN_API_KEY=your_key
   TELEGRAM_BOT_TOKEN=your_token
   SLACK_BOT_TOKEN=your_token
   SLACK_SIGNING_SECRET=your_secret
   ```
5. Enable Persistent Disk for `/data`

### Dashboard on Streamlit Cloud

1. Visit https://streamlit.io/cloud
2. Connect GitHub repo
3. Main file: `dashboard/app.py`
4. Environment: `BACKEND_URL=https://your-backend.onrender.com`

### Webhook Configuration

After deployment, update webhooks:
- Telegram: Set webhook to `https://your-backend.onrender.com/webhook/telegram`
- Slack: Update Request URL to `https://your-backend.onrender.com/webhook/slack`

## Troubleshooting

- **Database not found**: Ensure `data/` directory exists
- **FAISS errors**: Check vector dimension matches (1536)
- **Webhook timeout**: Increase response timeout in bot settings
