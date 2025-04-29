import sqlite3

conn = sqlite3.connect("database.sqlite3")
cursor = conn.cursor()

# Mostra o último usuário registrado
cursor.execute("SELECT id, public_key FROM users ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()

print("ID:", row[0])
print("CHAVE (repr):")
print(repr(row[1]))  # Mostra quebras de linha como \n

print("\nCHAVE (com delimitadores):")
print(">" + row[1] + "<")  # Delimita visualmente

conn.close()
