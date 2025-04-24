import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "database.sqlite3"

def insert_artwork(author_id: int, file_hash: str, title: str, description: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_utc_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO artworks (author_id, hash, title, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (author_id, file_hash, title, description, now_utc_iso))
    artwork_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artwork_id

def get_artwork_by_id(artwork_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, author_id, hash, title, description, created_at
        FROM artworks WHERE id = ?
    """, (artwork_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "author_id": row[1],
            "hash": row[2],
            "title": row[3],
            "description": row[4],
            "created_at": row[5],
        }
    return None

def list_artworks(author_id: Optional[int] = None,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, author_id, hash, title, description, created_at FROM artworks WHERE 1=1"
    params = []
    if author_id:
        query += " AND author_id = ?"
        params.append(author_id)
    if date_from:
        query += " AND created_at >= ?"
        params.append(date_from)
    if date_to:
        query += " AND created_at <= ?"
        params.append(date_to)
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "author_id": r[1], "hash": r[2],
            "title": r[3], "description": r[4], "created_at": r[5]
        } for r in rows
    ]
