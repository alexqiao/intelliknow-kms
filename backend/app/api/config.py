from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, FrontendConfig
from pydantic import BaseModel
import json

router = APIRouter()

class FrontendConfigCreate(BaseModel):
    platform: str
    credentials: dict
    enabled: bool = True

@router.get("/config/frontend/{platform}")
async def get_frontend_config(platform: str, db: Session = Depends(get_db)):
    config = db.query(FrontendConfig).filter(FrontendConfig.platform == platform).first()
    if not config:
        return {"platform": platform, "enabled": False, "credentials": {}}
    return {
        "platform": config.platform,
        "enabled": config.enabled,
        "credentials": json.loads(config.credentials),
        "status": config.status
    }

@router.post("/config/frontend")
async def save_frontend_config(config: FrontendConfigCreate, db: Session = Depends(get_db)):
    existing = db.query(FrontendConfig).filter(FrontendConfig.platform == config.platform).first()

    if existing:
        existing.credentials = json.dumps(config.credentials)
        existing.enabled = config.enabled
        existing.status = "active"
    else:
        new_config = FrontendConfig(
            platform=config.platform,
            credentials=json.dumps(config.credentials),
            enabled=config.enabled,
            status="active"
        )
        db.add(new_config)

    db.commit()
    return {"ok": True, "platform": config.platform}

@router.post("/config/frontend/{platform}/test")
async def test_frontend_config(platform: str, db: Session = Depends(get_db)):
    config = db.query(FrontendConfig).filter(FrontendConfig.platform == platform).first()
    if not config:
        raise HTTPException(404, "Config not found")

    creds = json.loads(config.credentials)

    if platform == "telegram":
        from app.services.telegram_client import TelegramClient
        client = TelegramClient(creds.get("bot_token"))
        try:
            chat_id = creds.get("admin_chat_id")
            if chat_id:
                await client.send_message(int(chat_id), "✅ Connection Successful!")
                return {"ok": True, "message": "Test message sent"}
            return {"ok": False, "message": "Admin chat ID not configured"}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    elif platform == "slack":
        from app.services.slack_client import SlackClient
        client = SlackClient(creds.get("bot_token"), creds.get("signing_secret"))
        try:
            channel = creds.get("admin_channel")
            if channel:
                await client.send_message(channel, "✅ Connection Successful!")
                return {"ok": True, "message": "Test message sent"}
            return {"ok": False, "message": "Admin channel not configured"}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    return {"ok": False, "message": "Unknown platform"}
