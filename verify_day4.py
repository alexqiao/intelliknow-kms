#!/usr/bin/env python3
"""Day 4 前端集成验证"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def verify_integration():
    from app.database import SessionLocal, QueryLog
    from app.config import get_settings

    print("🧪 Day 4 前端集成验证\n")

    settings = get_settings()
    db = SessionLocal()

    # 1. 检查配置
    print("1️⃣ 配置检查:")
    print(f"   ✓ Telegram Token: {settings.telegram_bot_token[:20]}...")
    print(f"   ✓ Slack Token: {settings.slack_bot_token[:20]}...")

    # 2. 检查查询日志
    print("\n2️⃣ 查询日志统计:")
    telegram_logs = db.query(QueryLog).filter(QueryLog.frontend_source == "telegram").count()
    slack_logs = db.query(QueryLog).filter(QueryLog.frontend_source == "slack").count()
    print(f"   Telegram: {telegram_logs} 条查询")
    print(f"   Slack: {slack_logs} 条查询")

    # 3. 响应时间
    print("\n3️⃣ 性能指标:")
    all_logs = db.query(QueryLog).all()
    if all_logs:
        avg_time = sum(l.response_time_ms for l in all_logs) / len(all_logs)
        print(f"   平均响应时间: {avg_time:.0f}ms")
        print(f"   ✓ {'符合' if avg_time < 3000 else '超过'} <3s 要求")

    db.close()
    print("\n✅ Day 4 验证完成！")

if __name__ == "__main__":
    verify_integration()
