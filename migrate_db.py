#!/usr/bin/env python3
"""数据库迁移：添加 access_count 字段"""
import sqlite3
import os

db_path = "backend/data/intelliknow.db"

if not os.path.exists(db_path):
    print("❌ 数据库文件不存在")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查 access_count 字段是否存在
cursor.execute("PRAGMA table_info(documents)")
columns = [col[1] for col in cursor.fetchall()]

if "access_count" not in columns:
    print("📝 添加 access_count 字段...")
    cursor.execute("ALTER TABLE documents ADD COLUMN access_count INTEGER DEFAULT 0")
    conn.commit()
    print("✅ 字段添加成功")
else:
    print("✓ access_count 字段已存在")

conn.close()
print("\n✅ 数据库迁移完成")
