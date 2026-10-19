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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY,
    input_text TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    dataset_id INTEGER NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
    )
    """)

    connection.commit()
    connection.close()

def get_database_connection():
    connection = sqlite3.connect("releaseguard.db")
    return connection