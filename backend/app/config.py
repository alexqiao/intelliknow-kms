from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    qwen_api_key: str
    database_url: str = "sqlite:///./data/intelliknow.db"
    telegram_bot_token: str = ""
    slack_bot_token: str = ""
    slack_signing_secret: str = ""

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

@lru_cache()
def get_settings():
    return Settings()
