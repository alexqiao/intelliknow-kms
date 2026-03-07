#!/usr/bin/env python3
"""初始化默认意图"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal, Intent

def init_default_intents():
    db = SessionLocal()

    # 检查是否已有意图
    existing = db.query(Intent).count()
    if existing > 0:
        print(f"✓ 已存在 {existing} 个意图，跳过初始化")
        db.close()
        return

    # 创建默认意图
    default_intents = [
        {
            "name": "HR",
            "description": "Human Resources related queries about policies, benefits, leave, recruitment",
            "keywords": "vacation,leave,policy,benefits,salary,recruitment,employee,HR,人力资源,休假,福利,薪资"
        },
        {
            "name": "Legal",
            "description": "Legal and compliance related queries about contracts, regulations, terms",
            "keywords": "contract,legal,compliance,regulation,terms,law,agreement,法律,合同,合规,条款"
        },
        {
            "name": "Finance",
            "description": "Finance and accounting related queries about budget, expenses, invoices",
            "keywords": "budget,expense,invoice,payment,accounting,finance,cost,财务,预算,费用,发票,报销"
        }
    ]

    for intent_data in default_intents:
        intent = Intent(**intent_data)
        db.add(intent)
        print(f"✓ 创建意图: {intent_data['name']}")

    db.commit()
    db.close()
    print("\n✅ 默认意图初始化完成！")

if __name__ == "__main__":
    init_default_intents()
