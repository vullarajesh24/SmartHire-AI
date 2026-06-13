import sqlite3

conn = sqlite3.connect("smarthire.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score INTEGER
)
""")

print("Database Created Successfully")

conn.commit()

conn.close()