#!/usr/bin/env python3
"""测试 Slack 集成"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_slack():
    from app.services.slack_client import SlackClient
    from app.config import get_settings

    print("🧪 测试 Slack 集成\n")

    settings = get_settings()

    if not settings.slack_bot_token:
        print("❌ SLACK_BOT_TOKEN 未配置")
        return

    print(f"✓ Token: {settings.slack_bot_token[:20]}...")
    print(f"✓ Signing Secret: {settings.slack_signing_secret[:20]}...")

    slack_client = SlackClient(settings.slack_bot_token, settings.slack_signing_secret)

    # 测试发送消息（需要提供实际的 channel ID）
    print("\n📝 Slack 客户端初始化成功")
    print("⚠️  需要在 Slack App 中配置 Event Subscriptions:")
    print(f"   Request URL: https://your-ngrok-url/webhook/slack")
    print("   Subscribe to: message.channels")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_slack())
