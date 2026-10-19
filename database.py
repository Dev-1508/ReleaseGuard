import sqlite3

connection = sqlite3.connect("releaseguard.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")

#cursor.execute(
 #   "INSERT INTO projects (name) VALUES (?)",
  #  ("Customer support Agent",)
#)

cursor.execute("SELECT * FROM projects")
rows = cursor.fetchall()
print(rows)

connection.commit()
connection.close()