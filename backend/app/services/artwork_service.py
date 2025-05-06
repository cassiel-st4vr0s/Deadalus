import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone
from schemas.artwork import ArtworkRead
from pathlib import Path
from fastapi import HTTPException

DB_PATH = Path(__file__).resolve().parents[1] / "database.sqlite3"

def insert_artwork(author_id: int, file_hash: str, title: str, description: str, preview_path: str, author_name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_utc_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute(""" 
        INSERT INTO artworks (author_id, file_hash, title, description, created_at, preview_path, author_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (author_id, file_hash, title, description, now_utc_iso, preview_path, author_name))
    artwork_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artwork_id



def get_artwork_by_id(artwork_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, author_id, file_hash, title, description, created_at
        FROM artworks WHERE id = ?
    """, (artwork_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "author_id": row[1],
            "file_hash": row[2],
            "title": row[3],
            "description": row[4],
            "created_at": row[5],
        }
    return None


def list_artworks(
    title: Optional[str] = None,
    author_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query base com JOIN para pegar o nome do autor
    query = """
    SELECT a.id, a.author_id, u.name as author_name, 
           a.file_hash, a.title, a.description, a.created_at, a.preview_path 
    FROM artworks a
    LEFT JOIN users u ON a.author_id = u.id
    WHERE 1=1
    """
    
    params = []
    
    if title:
        query += " AND a.title LIKE ?"
        params.append(f"%{title}%")
    if author_id:
        query += " AND a.author_id = ?"
        params.append(author_id)
    if date_from:
        query += " AND a.created_at >= ?"
        params.append(date_from)
    if date_to:
        query += " AND a.created_at <= ?"
        params.append(date_to)
    
    query += " ORDER BY a.created_at DESC"
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0], 
            "author_id": r[1], 
            "author_name": r[2],
            "file_hash": r[3], 
            "title": r[4], 
            "description": r[5], 
            "created_at": r[6],
            "preview_path": r[7]
        } for r in rows
    ]
    
def get_artwork_with_token(artwork_id: int) -> dict:
    """Obtém os dados da obra junto com informações do token associado"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Busca a obra e o token associado (se existir)
    cursor.execute("""
        SELECT 
            a.id, a.title, a.description, a.preview_path,
            t.id as token_id, t.price_tokens, t.status,
            u.name as author_name
        FROM artworks a
        LEFT JOIN tokens t ON a.id = t.artwork_id
        LEFT JOIN users u ON a.author_id = u.id
        WHERE a.id = ?
    """, (artwork_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Obra não encontrada")
    
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "preview_path": row[3],
        "token": {
            "id": row[4],
            "price": row[5],
            "status": row[6]
        } if row[4] else None,
        "author_name": row[7]
    }    

def get_artworks_by_author_id(author_id: int) -> List[ArtworkRead]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, description, file_hash, author_id, created_at, author_name, preview_path
        FROM artworks
        WHERE author_id = ?
        """,
        (author_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    
    # Se há resultados, converta-os em uma lista de objetos ArtworkRead
    if rows:
        return [
            ArtworkRead(
                id=row[0],
                title=row[1],
                description=row[2],
                file_hash=row[3],
                author_id=row[4],
                created_at=row[5],
                author_name=row[6],  # Adicionando author_name
                preview_path=row[7]   # Adicionando preview_path
            )
            for row in rows
        ]
    return []
