import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

# caminho para o banco de dados
DB_PATH = Path(__file__).resolve().parents[1] / "database.sqlite3"


def insert_token(artwork_id: int, owner_id: int, price_tokens: int, status: str = "available") -> int:
    """
    Insere um novo token na tabela `tokens` e retorna o token_id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tokens (artwork_id, owner_id, price_tokens, status, issued_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (artwork_id, owner_id, price_tokens, status, datetime.utcnow().isoformat()),
    )
    token_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return token_id

def update_token_status(token_id: int, status: str) -> None:
    """
    Atualiza o status do token no banco de dados.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tokens
        SET status = ?
        WHERE id = ?
        """,
        (status, token_id),
    )
    conn.commit()
    conn.close()


def get_token_by_id(token_id: int) -> Optional[dict]:
    """
    Busca um token pelo ID. Retorna dicionário ou None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, artwork_id, owner_id, price_tokens, status, issued_at
        FROM tokens
        WHERE id = ?
        """,
        (token_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "artwork_id": row[1],
            "owner_id": row[2],
            "price_tokens": row[3],  # Adicionando o campo price_tokens
            "status": row[4],
            "issued_at": row[5],
        }
    return None
