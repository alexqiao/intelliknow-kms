#!/usr/bin/env python3
"""
Migration script to add file_size column to documents table
"""
import sqlite3
import os

def migrate_add_file_size():
    db_path = "backend/data/intelliknow.db"

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if file_size column already exists
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]

    if "file_size" in columns:
        print("✓ file_size column already exists")
    else:
        print("Adding file_size column to documents table...")
        cursor.execute("ALTER TABLE documents ADD COLUMN file_size INTEGER DEFAULT 0")
        conn.commit()
        print("✓ file_size column added successfully")

    # Update file_size for existing documents
    cursor.execute("SELECT id, file_path FROM documents WHERE file_size = 0 OR file_size IS NULL")
    docs = cursor.fetchall()

    if docs:
        print(f"\nUpdating file sizes for {len(docs)} existing documents...")
        for doc_id, file_path in docs:
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                cursor.execute("UPDATE documents SET file_size = ? WHERE id = ?", (file_size, doc_id))
                print(f"  - Document ID {doc_id}: {file_size} bytes")
            else:
                print(f"  - Document ID {doc_id}: File not found, keeping size as 0")

        conn.commit()
        print("✓ File sizes updated successfully")
    else:
        print("No documents need file size updates")

    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_add_file_size()
