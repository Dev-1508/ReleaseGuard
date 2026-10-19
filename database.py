import sqlite3


def initialize_database():
    connection = sqlite3.connect("releaseguard.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()