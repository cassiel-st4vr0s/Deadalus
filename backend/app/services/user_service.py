import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "database.sqlite3"

def insert_user(name: str, public_key: str, private_key_encrypted: str, email: str, password_hash: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_utc_iso = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        INSERT INTO users (name, public_key, private_key_encrypted, email, password_hash, registered_at, wallet_balance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, public_key, private_key_encrypted, email, password_hash, now_utc_iso, 100))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, public_key, registered_at, wallet_balance FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "public_key": row[2],
            "registered_at": row[3],
            "wallet_balance": row[4]  # Inclui o saldo da carteira
        }
    return None

def get_user_by_email(email: str) -> Optional[dict]:
    """
    Busca um usuário pelo email no banco de dados.
    Retorna um dicionário com os dados do usuário ou None se não encontrado.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, email, password_hash, wallet_balance, private_key_encrypted FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "password_hash": user[3],
            "wallet_balance": user[4],
            "private_key_encrypted": user[5],  # <- Adicionado
        }
    else:
        return None

    
def update_user_wallet(user_id: int, new_balance: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET wallet_balance = ? WHERE id = ?
    """, (new_balance, user_id))
    conn.commit()
    conn.close()

