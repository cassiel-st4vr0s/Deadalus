import sqlite3
from pathlib import Path

# Caminho para o banco
DB_PATH = Path(__file__).resolve().parent / "database.sqlite3"

# Cria conexão
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  public_key TEXT UNIQUE NOT NULL,
  registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS artworks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  hash TEXT NOT NULL,
  title TEXT,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(author_id) REFERENCES users(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artwork_id INTEGER NOT NULL,
  owner_id INTEGER NOT NULL,
  status TEXT CHECK(status IN ('available','sold','burned')) NOT NULL DEFAULT 'available',
  issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(artwork_id) REFERENCES artworks(id),
  FOREIGN KEY(owner_id) REFERENCES users(id)
);
""")

conn.commit()

# Validação: listar tabelas existentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabelas no banco de dados:")
for table in tables:
    print(f"- {table[0]}")

conn.close()
print("Migração concluída. Banco de dados criado/modificado com sucesso.")
