import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "database.sqlite3"

def insert_user(name: str, public_key: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_utc_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO users (name, public_key, registered_at)
        VALUES (?, ?, ?)
    """, (name, public_key, now_utc_iso))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, public_key, registered_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "public_key": row[2],
            "registered_at": row[3]
        }
    return None
