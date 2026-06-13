import sqlite3

conn = sqlite3.connect("smarthire.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM scores WHERE username IS NULL")

conn.commit()

print("NULL usernames deleted!")

conn.close()