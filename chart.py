import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("smarthire.db")
cursor = conn.cursor()

cursor.execute("SELECT score FROM scores")
scores = [row[0] for row in cursor.fetchall()]

conn.close()

plt.figure(figsize=(6,4))
plt.hist(scores)

plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Number of Attempts")

plt.show()