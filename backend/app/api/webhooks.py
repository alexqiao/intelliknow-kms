from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db, FrontendConfig
from app.services.orchestrator import QueryOrchestrator
from app.services.telegram_client import TelegramClient
from app.services.slack_client import SlackClient
from app.services.llm_service import QwenLLMService
from app.services.vector_store import VectorStore
from app.config import get_settings
from app.utils.formatters import format_for_telegram, format_for_slack
from app.utils.security import sanitize_input
import json

router = APIRouter()
settings = get_settings()

llm_service = QwenLLMService(settings.qwen_api_key)
vector_store = VectorStore(dimension=1024)

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(f"📨 Telegram webhook received: {data}")

        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = sanitize_input(message.get("text", ""))
        user_id = str(message.get("from", {}).get("id"))

        if not chat_id or not text:
            print("⚠️  Missing chat_id or text")
            return {"ok": True}

        print(f"💬 Processing query: {text}")
        orchestrator = QueryOrchestrator(llm_service, vector_store, db)
        result = await orchestrator.process_query(text, "telegram", user_id)

        print(f"✅ Response generated: {result['response'][:50]}...")

        # Get token from database
        config = db.query(FrontendConfig).filter(FrontendConfig.platform == "telegram").first()
        if config and config.enabled:
            creds = json.loads(config.credentials)
            telegram_client = TelegramClient(creds.get("bot_token"))
        else:
            telegram_client = TelegramClient(settings.telegram_bot_token)

        formatted_msg = format_for_telegram(result["response"], result["intent"], result["confidence"])
        await telegram_client.send_message(chat_id, formatted_msg)
        print(f"📤 Message sent to chat {chat_id}")

        return {"ok": True}
    except Exception as e:
        print(f"❌ Error in telegram webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

@router.post("/webhook/slack")
async def slack_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}

    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        channel = event.get("channel")
        text = sanitize_input(event.get("text", ""))
        user_id = event.get("user")

        orchestrator = QueryOrchestrator(llm_service, vector_store, db)
        result = await orchestrator.process_query(text, "slack", user_id)

        # Get token from database
        config = db.query(FrontendConfig).filter(FrontendConfig.platform == "slack").first()
        if config and config.enabled:
            creds = json.loads(config.credentials)
            slack_client = SlackClient(creds.get("bot_token"), creds.get("signing_secret"))
        else:
            slack_client = SlackClient(settings.slack_bot_token, settings.slack_signing_secret)

        formatted_msg = format_for_slack(result["response"], result["intent"], result["confidence"])
        await slack_client.send_message(channel, formatted_msg)

    return {"ok": True}
